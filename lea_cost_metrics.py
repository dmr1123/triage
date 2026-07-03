#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lea_cost_metrics.py — 零 GPU 成本/指標離線計算器(LEA 環境向量實驗用)

吃「逐題 JSON log」目錄,輸出:
  * 每臂成本表 C1–C4/C7/C9(markdown + LaTeX)
  * 新效能指標 P1 full-set recall / P2 首版計畫覆蓋 / P3 冗餘呼叫率 /
    P4 calls-per-gold / P5 off-server 率(欄位存在才算,缺欄自動跳過並列示)
  * 任兩臂 paired bootstrap(10k)+ Wilcoxon signed-rank + Holm 校正
  * 成本–效能 Pareto 前緣 CSV

輸入格式(канonical;缺欄容忍):每題一個 .json,或一個 .jsonl 每行一題:
{
  "task_id": "math_035", "arm": "combo",
  "gold_tools": ["a","b"], "called_tools": ["a","x","a","b"],
  "first_plan_tools": ["a"],                 # 第 1 輪 plan 涵蓋的工具(可選)
  "llm_calls": 42, "tool_calls": 9,
  "prompt_tokens": 18000, "completion_tokens": 2100,   # 缺→用 *_chars/4 估
  "prompt_chars": null, "completion_chars": null,
  "wall_s": 210.5,
  "off_server_calls": 1,                     # 可選
  "select_hits": 5, "select_total": 6,       # BGE top-5 內含 gold 的行數(可選)
  "extra_ctx_tokens": 0                      # 該臂每次規劃額外注入的 context(card/top5/icl)
}
別名自動對應:gold/golds→gold_tools、calls/toolcalls→tool_calls、
llm_call_count→llm_calls、trajectory→called_tools(取其中 tool 欄)等,見 ALIASES。

用法:
  python lea_cost_metrics.py --scan runs/ --out cost_tables/ [--clean-list clean20.txt]
  python lea_cost_metrics.py --selftest        # 內建合成資料驗證(無需任何檔案)
穩定性:僅用標準函式庫;bootstrap 固定 seed 可重現。
"""
import argparse, json, math, os, random, sys, csv
from collections import defaultdict

ALIASES = {
    "gold_tools": ["gold_tools", "gold", "golds", "gold_set", "required_tools"],
    "called_tools": ["called_tools", "called", "calls_list", "tools_called", "call_sequence"],
    "first_plan_tools": ["first_plan_tools", "first_plan", "plan0_tools"],
    "llm_calls": ["llm_calls", "llm_call_count", "n_llm_calls"],
    "tool_calls": ["tool_calls", "toolcalls", "n_tool_calls", "num_calls"],
    "prompt_tokens": ["prompt_tokens", "in_tokens", "input_tokens"],
    "completion_tokens": ["completion_tokens", "out_tokens", "output_tokens"],
    "prompt_chars": ["prompt_chars"], "completion_chars": ["completion_chars"],
    "wall_s": ["wall_s", "wall_clock_s", "elapsed_s", "duration_s"],
    "off_server_calls": ["off_server_calls", "off_srv_calls", "offserver"],
    "select_hits": ["select_hits"], "select_total": ["select_total"],
    "extra_ctx_tokens": ["extra_ctx_tokens", "env_ctx_tokens"],
    "task_id": ["task_id", "id", "task"], "arm": ["arm", "method", "system"],
}

def _get(d, key, default=None):
    for k in ALIASES.get(key, [key]):
        if k in d and d[k] is not None:
            return d[k]
    return default

def load_records(path):
    recs = []
    for root, _, files in os.walk(path):
        for fn in files:
            fp = os.path.join(root, fn)
            try:
                if fn.endswith(".jsonl"):
                    with open(fp, encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line:
                                recs.append(json.loads(line))
                elif fn.endswith(".json"):
                    with open(fp, encoding="utf-8") as f:
                        obj = json.load(f)
                    recs.extend(obj if isinstance(obj, list) else [obj])
            except Exception as e:
                print(f"[warn] skip {fp}: {e}", file=sys.stderr)
    return recs

def normalize(rec):
    r = {}
    for k in ALIASES:
        r[k] = _get(rec, k)
    # called_tools 容忍 trajectory 物件列表
    ct = r["called_tools"]
    if ct and isinstance(ct[0], dict):
        r["called_tools"] = [c.get("tool") or c.get("name") for c in ct]
    # token 缺 → 字元/4 估(標記口徑)
    r["tok_est"] = False
    if r["prompt_tokens"] is None and r["prompt_chars"] is not None:
        r["prompt_tokens"] = r["prompt_chars"] / 4.0; r["tok_est"] = True
    if r["completion_tokens"] is None and r["completion_chars"] is not None:
        r["completion_tokens"] = r["completion_chars"] / 4.0; r["tok_est"] = True
    return r

# ---------------- 指標 ----------------
def task_metrics(r):
    m = {}
    gold, called = r["gold_tools"], r["called_tools"]
    if gold and called is not None:
        gset, cset = set(gold), set(called)
        m["gold_recall"] = len(gset & cset) / len(gset)
        m["full_set"] = 1.0 if gset <= cset else 0.0             # P1
        if r["tool_calls"] is None:
            r["tool_calls"] = len(called)
        hit = len(gset & cset)
        m["calls_per_gold"] = (r["tool_calls"] / hit) if hit else float("inf")  # P4
        dup = len(called) - len(set(map(str, called)))
        useless = sum(1 for c in called if c not in gset)
        m["redundant_rate"] = (dup + useless) / max(len(called), 1)            # P3(保守口徑:重複+非gold)
    if gold and r["first_plan_tools"] is not None:
        m["first_plan_cov"] = len(set(gold) & set(r["first_plan_tools"])) / len(set(gold))  # P2
    if r["off_server_calls"] is not None and r["tool_calls"]:
        m["off_server_rate"] = r["off_server_calls"] / r["tool_calls"]         # P5
    if r["select_hits"] is not None and r["select_total"]:
        m["select_hit_rate"] = r["select_hits"] / r["select_total"]            # P6
    for c in ["llm_calls", "tool_calls", "prompt_tokens", "completion_tokens",
              "wall_s", "extra_ctx_tokens"]:
        if r[c] is not None:
            m[c] = float(r[c])
    if "gold_recall" in m and m.get("completion_tokens"):
        m["recall_per_1k_out"] = m["gold_recall"] / (m["completion_tokens"] / 1000.0)  # C9
    return m

METRIC_ORDER = ["gold_recall", "full_set", "first_plan_cov", "redundant_rate",
                "calls_per_gold", "off_server_rate", "select_hit_rate",
                "llm_calls", "tool_calls", "prompt_tokens", "completion_tokens",
                "extra_ctx_tokens", "wall_s", "recall_per_1k_out"]

# ---------------- 統計 ----------------
def mean(xs): return sum(xs) / len(xs) if xs else float("nan")

def boot_ci(xs, iters=10000, seed=7):
    if not xs: return (float("nan"),) * 2
    rng = random.Random(seed); n = len(xs); ms = []
    for _ in range(iters):
        ms.append(mean([xs[rng.randrange(n)] for _ in range(n)]))
    ms.sort()
    return ms[int(0.025 * iters)], ms[int(0.975 * iters)]

def paired_bootstrap(a, b, iters=10000, seed=7):
    """回傳 (mean_diff, ci_lo, ci_hi, p_two_sided);a/b 為同題配對序列。"""
    diffs = [x - y for x, y in zip(a, b)]
    rng = random.Random(seed); n = len(diffs); ds = []
    for _ in range(iters):
        ds.append(mean([diffs[rng.randrange(n)] for _ in range(n)]))
    ds.sort()
    d = mean(diffs)
    ge = sum(1 for x in ds if x >= 0); le = sum(1 for x in ds if x <= 0)
    p = 2 * min(ge, le) / iters
    return d, ds[int(0.025 * iters)], ds[int(0.975 * iters)], min(p, 1.0)

def wilcoxon(a, b):
    """signed-rank,常態近似(n≥10 才可靠);回傳 (W, p_two_sided)。"""
    diffs = [x - y for x, y in zip(a, b) if x != y]
    n = len(diffs)
    if n == 0: return 0.0, 1.0
    ranked = sorted((abs(d), d) for d in diffs)
    ranks, i = {}, 0
    while i < len(ranked):
        j = i
        while j + 1 < len(ranked) and ranked[j + 1][0] == ranked[i][0]:
            j += 1
        r = (i + j) / 2 + 1
        for k in range(i, j + 1): ranks[k] = r
        i = j + 1
    wplus = sum(ranks[k] for k, (_, d) in enumerate(ranked) if d > 0)
    mu = n * (n + 1) / 4; sd = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
    z = (wplus - mu) / sd if sd else 0.0
    p = math.erfc(abs(z) / math.sqrt(2))
    return wplus, p

def holm(pvals):
    """輸入 {name: p};回傳 {name: p_adj}(Holm–Bonferroni)。"""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items); out = {}; running = 0.0
    for i, (k, p) in enumerate(items):
        adj = min((m - i) * p, 1.0); running = max(running, adj); out[k] = running
    return out

# ---------------- 匯總與輸出 ----------------
def aggregate(records, clean_ids=None):
    per_arm = defaultdict(dict)     # arm -> task_id -> metrics
    for rec in records:
        r = normalize(rec)
        if not r["arm"] or not r["task_id"]: continue
        if clean_ids and r["task_id"] not in clean_ids: continue
        per_arm[r["arm"]][r["task_id"]] = task_metrics(r)
    return per_arm

def fmt(x):
    if x is None or (isinstance(x, float) and math.isnan(x)): return "—"
    if isinstance(x, float) and math.isinf(x): return "∞"
    return f"{x:.3f}" if abs(x) < 10 else f"{x:.1f}"

def arm_table(per_arm, out_dir):
    arms = sorted(per_arm)
    lines_md = ["| 指標 | " + " | ".join(arms) + " |",
                "|---" * (len(arms) + 1) + "|"]
    lines_tex = []
    for met in METRIC_ORDER:
        row = [met]
        for a in arms:
            xs = [m[met] for m in per_arm[a].values() if met in m and not math.isinf(m[met])]
            if xs:
                lo, hi = boot_ci(xs)
                row.append(f"{fmt(mean(xs))} [{fmt(lo)},{fmt(hi)}] (n={len(xs)})")
            else:
                row.append("—")
        lines_md.append("| " + " | ".join(row) + " |")
        lines_tex.append(" & ".join(row) + r" \\")
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, "arm_table.md"), "w", encoding="utf-8").write("\n".join(lines_md))
    open(os.path.join(out_dir, "arm_table.tex"), "w", encoding="utf-8").write("\n".join(lines_tex))
    return lines_md

def pairwise(per_arm, metric, ref, out_dir):
    if ref not in per_arm: return []
    res, pvals = [], {}
    for a in sorted(per_arm):
        if a == ref: continue
        common = sorted(set(per_arm[a]) & set(per_arm[ref]))
        aa = [per_arm[a][t].get(metric) for t in common]
        bb = [per_arm[ref][t].get(metric) for t in common]
        pairs = [(x, y) for x, y in zip(aa, bb) if x is not None and y is not None]
        if len(pairs) < 3: continue
        x, y = zip(*pairs)
        d, lo, hi, p = paired_bootstrap(list(x), list(y))
        _, pw = wilcoxon(list(x), list(y))
        res.append((a, len(pairs), d, lo, hi, p, pw)); pvals[a] = p
    adj = holm(pvals)
    lines = [f"# paired vs `{ref}` on `{metric}`",
             "| arm | n | Δmean | 95% CI | p(boot) | p(Holm) | p(Wilcoxon) |",
             "|---|---|---|---|---|---|---|"]
    for a, n, d, lo, hi, p, pw in res:
        lines.append(f"| {a} | {n} | {fmt(d)} | [{fmt(lo)},{fmt(hi)}] | {p:.4f} | {adj[a]:.4f} | {pw:.4f} |")
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, f"paired_{metric}_vs_{ref}.md"), "w", encoding="utf-8").write("\n".join(lines))
    return lines

def pareto_csv(per_arm, out_dir):
    rows = [("arm", "completion_tokens_mean", "gold_recall_mean")]
    for a in sorted(per_arm):
        ct = [m["completion_tokens"] for m in per_arm[a].values() if "completion_tokens" in m]
        gr = [m["gold_recall"] for m in per_arm[a].values() if "gold_recall" in m]
        if ct and gr: rows.append((a, f"{mean(ct):.1f}", f"{mean(gr):.4f}"))
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "pareto.csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

# ---------------- 自測 ----------------
def selftest():
    rng = random.Random(0); recs = []
    for arm, base, tok in [("frozen", 0.80, 1500), ("combo", 0.92, 2100)]:
        for i in range(20):
            gold = ["g1", "g2", "g3"]
            hit = 3 if rng.random() < base else 2
            called = gold[:hit] + ["x"] * rng.randrange(0, 3)
            recs.append({"task_id": f"t{i:02d}", "arm": arm, "gold_tools": gold,
                         "called_tools": called, "first_plan_tools": gold[:max(hit - 1, 1)],
                         "llm_calls": 28 if arm == "frozen" else 42,
                         "tool_calls": len(called), "completion_tokens": tok + rng.randrange(-100, 100),
                         "wall_s": 100 + rng.random() * 20, "extra_ctx_tokens": 0})
    per_arm = aggregate(recs)
    t = arm_table(per_arm, "/tmp/lea_selftest")
    pw = pairwise(per_arm, "gold_recall", "frozen", "/tmp/lea_selftest")
    pareto_csv(per_arm, "/tmp/lea_selftest")
    # 斷言:指標方向正確
    fr = mean([m["gold_recall"] for m in per_arm["frozen"].values()])
    cb = mean([m["gold_recall"] for m in per_arm["combo"].values()])
    assert cb > fr, "combo 應高於 frozen(合成設定如此)"
    fs = mean([m["full_set"] for m in per_arm["combo"].values()])
    assert 0 <= fs <= 1
    a, b = [1, 2, 3, 4, 5], [1, 2, 3, 4, 5]
    d, lo, hi, p = paired_bootstrap(a, b); assert abs(d) < 1e-9 and p == 1.0
    print("\n".join(t[:6])); print(); print("\n".join(pw))
    print("\n[selftest OK] 指標與統計自洽;輸出在 /tmp/lea_selftest/")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan"); ap.add_argument("--out", default="cost_tables")
    ap.add_argument("--clean-list"); ap.add_argument("--ref", default="frozen")
    ap.add_argument("--metric", default="gold_recall")
    ap.add_argument("--pareto", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest: return selftest()
    if not args.scan: ap.error("--scan 或 --selftest 擇一")
    clean = None
    if args.clean_list:
        clean = {l.strip() for l in open(args.clean_list, encoding="utf-8") if l.strip()}
    per_arm = aggregate(load_records(args.scan), clean)
    if not per_arm:
        print("[err] 掃不到任何合法紀錄;檢查欄位別名(見檔頭 ALIASES)", file=sys.stderr); sys.exit(1)
    arm_table(per_arm, args.out)
    pairwise(per_arm, args.metric, args.ref, args.out)
    pareto_csv(per_arm, args.out)
    print(f"[done] {sum(len(v) for v in per_arm.values())} 題×臂 → {args.out}/")

if __name__ == "__main__":
    main()
