# Paper Draft — §5 Experiments(+§6 Cost Analysis)

> **使用說明(中文,不進論文)**:本章所有已填數字均取自你兩份研究文件(clean-20 v3 套件、G0–G3 gates、DEER 2×2);標 **⟨TBD⟩** 的格子等今夜 Phase 1/2 跑完、用 `lea_cost_metrics.py` 產表後填入。行文為投稿級英文;數字口徑(24 全量 vs clean-20)已在文中明確分開。措辭刻意用 "supports / outperforms",不用 "proves"。

---

## 5 Experiments

We evaluate whether a **zero-training environment vector**, injected at the activation level of a frozen planner, can match or exceed both (i) training-based adaptation and (ii) prompt-level environment injection, at equal or lower cost. All arms share the identical execution pipeline (grounding, argument filling, execution, synthesis; §4), so differences are attributable to the planning-stage environment mechanism alone.

### 5.1 Setup

**Benchmark and tasks.** We use synthesized multi-tool tasks over 10 stable MCP servers. We report on the full in-domain set of 24 tasks and, following our data-presence audit (§5.6), on a **clean-20** subset that removes four tasks whose questions reference data never provided; both views are always reported side by side. All tasks have solvability 9.0 under the benchmark's own grader.

**Model and pipeline.** The planner, selector, argument filler, and synthesizer are a single frozen Qwen2.5-7B-Instruct. Grounding uses a BGE-m3 index over per-tool *imagine sentences*. The v3 pipeline (chain-of-thought argument filling with self-check, resource registry, verified summarization, dependency-grouped wave plans) is shared by **all** arms; pipeline fixes are never exclusive to our method.

**Arms.**
- **frozen** — the shared pipeline with no environment injection (lower anchor).
- **cv-hybrid (ours)** — the contrastive environment vector (extracted from tool-list present/absent forward passes; zero training) injected during a *continue-writing* phase, with plan skeletons and termination owned by the frozen model.
- **combo (ours)** — 0.75·cv + 0.25·sv, adding a 25K-parameter synthetic discrimination vector trained in minutes on self-generated single-answer tasks (no trajectories, no benchmark data).
- **Training baselines** — trajectory-imitation adapter (LEA-traj, 5 seeds) and LoRA fine-tuning (3 seeds; plus LoRA on the same synthetic signal), representing weight-level adaptation.
- **Prompt baselines** — *env-card* (full tool list in context); **top-5-docs** ⟨TBD tonight⟩ (retrieved five tool documents in context, the strongest fair prompt-level competitor); **ICL-2shot** ⟨TBD tonight⟩ (two demonstration plans in context, the cheapest trajectory-based alternative).

**Metrics.** Objective, judge-free metrics are primary: **gold-recall** (fraction of required tools actually called), **full-set recall** (1 iff *all* required tools are called, cf. COMP@K), **first-plan coverage** (gold coverage of the very first plan, isolating planning boldness from multi-round self-healing), redundant-call rate, off-server rate, and calls-per-gold. A six-dimension rubric from a 32B judge is reported as secondary evidence with known biases documented (§5.6). Statistical testing uses paired bootstrap (10k resamples) with Holm–Bonferroni correction across arms; Wilcoxon signed-rank is reported as a robustness check.

### 5.2 Main results

**Table 1 — clean-20, v3 pipeline (primary).**

| Arm | gold-recall | full-set | first-plan cov. | 6-dim | LLM calls | p vs frozen (boot/Holm) |
|---|---|---|---|---|---|---|
| frozen | 0.842 | ⟨P0 tonight⟩ | ⟨P0⟩ | 0.859 | 28 | — |
| LoRA-synth / ctxd / mix | 0.879 / 0.871 / 0.835 | ⟨P0⟩ | ⟨P0⟩ | ~0.85 | 37–46 | all n.s. |
| env-card | 0.751* | ⟨P0⟩ | ⟨P0⟩ | 0.724* | ~frozen | n.s.* |
| **cv-hybrid (ours)** | 0.898 | ⟨P0⟩ | ⟨P0⟩ | 0.853 | 41 | ⟨recompute⟩ |
| **combo (ours)** | **0.915** | ⟨P0⟩ | ⟨P0⟩ | 0.852 | 42 | **p=0.003** |
| top-5-docs | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ |
| ICL-2shot | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ |

\*env-card numbers are from the 24-task v2 suite (its G2 evaluation); the clean-20 v3 rerun is queued with the two new prompt arms.

On clean-20, combo improves gold-recall by **+0.073 over frozen (p=0.003)** while both weight-level baselines are not significant, and prompt-level full-list injection *hurts*. On the earlier 24-task suite the ordering is identical (cv-hybrid 0.866 vs frozen 0.755, +0.111, p=0.009; five-seed trajectory imitation 0.754±0.035 and LoRA 0.755±0.024 both fail to beat frozen on any of the six rubric dimensions).

**Mechanism-vs-data control.** With the *same* synthetic signal, the vector-space variant is significant while LoRA is not, and mixing signals helps in vector space but cancels in weight space — supporting the claim that the effective ingredient is a low-rank activation direction, not the data.

### 5.3 Robustness (gates)

| Gate | Result |
|---|---|
| G0 significance | cv +0.111, CI [+0.016, +0.218], p=0.009; combo p=0.002 (24-task) |
| G1 extraction robustness | 4 disjoint query subsets → e2e 0.864±0.005 |
| G1b self-containment | vectors from synthetic queries only: 0.863 ≈ 0.866; direction cos 0.80–0.90 |
| G2 prompt-level control | full tool list in context: 0.751 ≈ frozen, 6-dim *below* frozen |
| G3 held-out servers | 3 unseen servers: ours 0.903–0.944 > frozen 0.875 > card 0.778 |

### 5.4 Cost analysis

**Table 2 — cost per arm (computed offline from execution logs; `lea_cost_metrics.py`).**

| Arm | one-time adaptation cost | assets | extra context / plan | LLM calls/task | tool calls/task | completion tok/task | recall per 1K out-tok |
|---|---|---|---|---|---|---|---|
| frozen | — | — | 0 | 28 | ⟨P0⟩ | ⟨P0⟩ | ⟨P0⟩ |
| LEA-traj / LoRA | teacher + rollouts + GPU·h ⟨fill from logs⟩ | MB-scale | 0 | 37–46 | ⟨P0⟩ | ⟨P0⟩ | ⟨P0⟩ |
| env-card | — | — | **+3–5K tok** | ~frozen | ⟨P0⟩ | ⟨P0⟩ | ⟨P0⟩ |
| top-5-docs | — | — | +⟨TBD, ~0.3–0.7K⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ |
| **cv (ours)** | ~80 forward passes, minutes, O(#tools) | **~100 KB** (7×hidden fp32) | **0** | 41 | 9.1 | ⟨P0⟩ | ⟨P0⟩ |
| **combo (ours)** | + minutes-level 25K-param vector | +100 KB | **0** | 42 | **7.8 (−15%)** | ⟨P0⟩ | ⟨P0⟩ |
| + DEER τ=0.95 | — | — | 0 | **−12%** | **−17%** | ⟨P0⟩ | ⟨P0⟩ |

The cost profile is the point: our adaptation is a **one-time, minutes-level, ~100 KB** artifact with **zero recurring context cost**, whereas prompt-level injection pays tokens on *every* planning call and training-level adaptation pays GPU-hours up front — and neither wins on quality. The confidence gate (DEER) turns the residual overhead into a knob: coverage-neutral at τ=0.95 (0.862 vs 0.866) with −17% tool calls / −12% LLM calls; crucially, the same gate *hurts* the frozen baseline (early-quitter type), corroborating that our arm's extra calls are over-work rather than flailing.

**Table 3 — context for the literature (reported numbers from the respective papers; different benchmarks, not directly comparable).** Prompt-level environment transfer costs tokens per call: full-schema stuffing averages 2,134 tokens vs. 1,084 with retrieval (RAG-MCP), or 6,308 vs. 111 with active requests (MCP-Zero). Activation-level control needs only KB-scale assets (ASA: ~20 KB). Our vectors follow the activation-level profile (~100 KB, zero context) while targeting environment knowledge for multi-step planning rather than single-step trigger control.

### 5.5 Ablations

1. **Dose.** cv+sv at full strength collapses (0.269); 0.75/0.25 is best — discrimination vectors are potent in small doses.
2. **Hybrid necessity.** Pure injection over-terminates on vague analytical tasks (math_035 → immediate DONE); the hybrid handoff makes premature termination *constructively impossible* and lower-bounds the arm at frozen.
3. **Orthogonality.** cos(cv, SGD-learned direction) ≈ 0 at every layer, yet the free direction performs better; cv, sv, and the learned direction are mutually near-orthogonal and composable in activation space (weight-space mixing cancels).
4. **Extraction budget.** ⟨P0: recompute from logs — vectors from 10/20/40 query pairs⟩.
5. **First-plan vs. self-healing.** ⟨P0: first-plan coverage isolates where the gain enters; prior proxy runs suggest re-planning washes out first-round differences, surfacing instead as −15% calls⟩.

### 5.6 Threats to validity

(i) **n=20/24**: the clean-20 margin (+0.056–0.073) reaches p=0.003 with the v3 pipeline but the 24-task margin loses significance after removing three data-absent tasks (p≈0.07); the scaled suite (n≈300 generated, data-presence-checked) is required before camera-ready. (ii) **Judge bias**: the rubric rewards volume and penalizes honest refusal; we therefore rank objective metrics first and report rubric deltas only within the same judge. (iii) **Single model/benchmark**: transfer to a second backbone and ToolBench-style tasks is planned; held-out-server results (G3) are the current out-of-distribution evidence. (iv) **Benchmark hygiene**: solvability graders miss data-absent tasks; we contribute a `data_check` filter and dual-report throughout.

---

## 今夜待辦對照(不進論文)
- P0 → 填 Table 1/2 的 ⟨P0⟩ 格與 §5.5(4)(5):`python lea_cost_metrics.py --scan runs/ --out cost_tables/`
- P1/P2 → 填 top-5-docs、ICL-2shot 兩列與 §5.4 其 context 成本
- 判讀句(先寫好,擇一保留):
  - 若 top5 ≈ frozen:*"Even a fair, retrieval-narrowed prompt injection fails to move a 7B planner, mirroring attention-dilution accounts of tool-selection failure."*
  - 若 top5 ≈ cv:*"Retrieval-narrowed prompting matches vector injection on quality; the remaining advantage of the vector is its zero recurring context cost."*
