# LEA 環境向量:成本 × 多指標實驗協定(今夜可執行版)

> 目的:把「我們的方法在**同成本或更低成本下**,勝過所有免軌跡基線」這個假設測到可發表的完整度。
> 措辭原則:實驗**支持**假設,不「證明」— 審稿語言用 supports / consistently outperforms。
> 執行地點:你的伺服器(`/home/wcs/depret`)。本文件 + `lea_cost_metrics.py` + 論文草稿由外部代理準備;**所有既有數字取自你的兩份研究文件,新格子一律標 ⟨TBD⟩,絕不虛構**。

---

## 0. 一夜的現實預算(先排優先級)

依你文件的既有節奏(clean-20 一臂 e2e + judge ≈ 單卡數小時):一夜實際可完成 **零 GPU 解析 + 2 個新臂 + 補 judge**。優先級:

| 優先 | 項目 | GPU | 預估 | 為什麼第一 |
|---|---|---|---|---|
| **P0** | 用 `lea_cost_metrics.py` 重解析**既有全部軌跡 log** → 完整成本表+新指標表 | 無 | ~1 小時 CPU | 零風險、立刻填滿論文成本章;所有臂(frozen/cv/combo/LoRA/card)一次到位 |
| **P1** | 新臂 A:**top-5 文件進 prompt**(審稿人最危險缺口) | 要 | ~2–3 小時 | env-card 是全清單 strawman;top-5 才是 RAG-MCP/檢索式的公平化身 |
| **P2** | 新臂 B:**few-shot ICL(2 條示範計畫)** | 要 | ~2–3 小時 | 「軌跡難收集」的最便宜反例,必須正面擊破 |
| **P3** | 兩新臂各 3 次重跑(pass^k 用) | 要 | 視餘裕 | 穩定性指標;不夠時間先 k=1 |
| P4(擇日) | ICV/FV 式抽取變體、隨機向量對照 | 要 | — | 機制消融,投稿前補 |

---

## 1. 指標套件

### 1.1 成本指標(全部可從既有 log 離線計算)

| # | 指標 | 定義/公式 | 來源欄位 |
|---|---|---|---|
| C1 | LLM calls / task | 規劃+select+填參+摘要+synth 全部呼叫數 | 執行器計數(你已有:frozen 28 vs combo 42) |
| C2 | Tool calls / task | 實際工具執行次數(你已有:9.12 vs 7.79;DEER −17%) | 同上 |
| C3 | Prompt / completion tokens per task | Σ 各呼叫(tokenizer 計)| log 或以字元/4 估算(標註口徑) |
| C4 | 環境注入的 context 成本 | card=每次規劃 +3–5K tok;**cv/sv=0** | 構造性 |
| C5 | 一次性抽取成本 | cv:~40×2 次 forward(O(#tools),分鐘級);sv:25K 參數、分鐘級;LoRA/traj:teacher+rollout+訓練(GPU·hr) | 紀錄 |
| C6 | 資產大小 | cv:7 層×hidden(fp32 ≈ 100KB);sv:25K;LoRA:MB 級 | 檔案大小 |
| C7 | Wall-clock / task、GPU·hr / 臂 | 直接計時 | 執行器 |
| C8 | $ / task(選報) | tokens×單價 或 GPU·hr×時價(附換算表) | C3/C7 |
| C9 | 成本正規化效能 | gold-recall ÷ (completion tokens/1K);success per GPU·hr | C1–C3+效能 |

### 1.2 新增效能指標(P0 可離線算的打 ●)

| # | 指標 | 定義 | 為什麼要加 |
|---|---|---|---|
| P1● | **Full-set recall(COMP 式)** | 該題 gold 工具**全部**叫齊=1,否則 0 | 比平均 gold-recall 嚴;COLT/TGR 都用此口徑,可比性 |
| P2● | **首版計畫覆蓋率** | 第 1 輪 plan 就涵蓋的 gold 比例 | 隔離「向量敢列全」vs「re-plan 自癒」(你已觀察到 proxy 增益被 5 輪自癒洗掉) |
| P3● | 冗餘呼叫率 | (重複 (tool,args) + 對 gold 無貢獻呼叫)/總呼叫 | 回應 judge 對「磨過頭」的量價懲罰 |
| P4● | Calls-per-gold | 總工具呼叫 ÷ 叫到的 gold 數 | 效率單一數字;DEER/sv 的賣點 |
| P5● | Off-server 率(已有) | 沿用 | — |
| P6● | 接地診斷:select 命中率 | gold 是否在 BGE top-5 內(逐行) | 把「檢索層 vs 規劃層」失分拆開 |
| P7 | **pass^k(k=3)** | 同題 3 次重跑全對才計 1(對 full-set recall) | τ-bench 口徑;審稿常問穩定性 |
| P8● | 參數/執行健全(已有,=1.00) | schema 合規、執行成功 | 當 sanity row |
| P9● | 六維 judge(已有) | 24 全量+clean-20 雙報 | — |
| P10● | 抽取穩健性(已有 0.864±0.005) | 4 子集重抽 | 零訓練方法的「seed」 |

### 1.3 統計協定
- 主檢定:**paired bootstrap 10k**(你已用)+ **Wilcoxon signed-rank** 佐證;多臂比較用 **Holm–Bonferroni** 校正(α=0.05)。
- 一律報 95% CI 與逐題配對差;n=20 的檢定力註記:偵測 +0.05 需 n≈80(與你的擴集計畫一致),清楚寫進 limitations。
- 兩臂共用管線版本(你的公平三則照抄進論文 protocol)。

---

## 2. 對照臂矩陣(狀態盤點)

| 臂 | 注入層 | 狀態 | 今夜 |
|---|---|---|---|
| frozen(+v3 修法) | — | ✅ 已有(0.842/28 calls) | 重解析 |
| cv-hybrid / combo(+sv) | activation | ✅ 已有(0.898 / **0.915** p=0.003) | 重解析 |
| LEA-traj7 / LoRA-FT / LoRA-synth | 權重 | ✅ 已有(全 n.s. 或負) | 重解析 |
| env-card(全清單) | prompt | ✅ 已有(0.751≈frozen) | 重解析 |
| **top-5 文件進 prompt** | prompt | ❌ **P1 今夜跑** | 新臂 A |
| **few-shot ICL(2 示範)** | prompt | ❌ **P2 今夜跑** | 新臂 B |
| ICV/FV 式抽取、隨機向量、幅度掃描 | activation | 部分(幅度已掃) | P4 擇日 |

### 新臂 A patch spec(top-5 docs;動最少的改法)
1. 規劃前:把整題 query 過 BGE 對 imagine 索引取 **top-5 工具**;
2. 在**兩臂共用的 SYS 規則集之後**附區塊:`Available tools (top-5 retrieved):` 每行 `imagine 句 — 一句參數摘要`(嚴格 ≤5 行,控制 context 在數百 token);
3. 其餘管線(select/fill_args/synth、四修法、共識重排)**完全不動**;DONE 權在 frozen。
4. 對照公平:此臂用它自己最舒服的 prompt(普通句式),不得綁 img-v2 嚴格格式(重蹈 B 臂灌水坑)。

### 新臂 B patch spec(ICL 2-shot)
1. 從**合成題**(非 benchmark)造 2 條完整示範:query→wave plan(含 `::` 與 `------`);
2. 附在 SYS 後、任務前;固定同 2 條(不做檢索式挑選,控制變因);
3. 記錄其 context 成本(預估 +400–700 tok/次規劃)進 C4。

---

## 3. 今夜 runbook(依序執行)

```bash
# Phase 0(零 GPU,~1hr):既有 log → 成本+新指標
python lea_cost_metrics.py --scan /home/wcs/depret/runs --out cost_tables/ \
    --arms frozen,cv_hybrid,combo,lora_synth,card --clean-list clean20.txt
#   產出:per-arm 成本表(C1–C9)、新指標表(P1–P6,P8)、配對 bootstrap、
#   markdown+LaTeX 兩版,直接貼論文 §5.4/§5.5

# Phase 1(GPU):新臂 A(top-5 docs)clean-20 + 24 全量
python lea_e2e_deer_v33.py --arm top5docs --tasks all24 --pipeline v3.3 --log runs/top5docs/
python run_judge32.sh runs/top5docs/

# Phase 2(GPU):新臂 B(ICL 2-shot)
python lea_e2e_deer_v33.py --arm icl2 --tasks all24 --pipeline v3.3 --log runs/icl2/

# Phase 3(視餘裕):兩新臂 ×3 重跑(pass^3)
# Phase 4(零 GPU):重跑 Phase 0 把新臂併進表;把數字填進論文草稿 ⟨TBD⟩ 格
```

> 判讀預期(先寫下、避免事後合理化):若 top5docs 落在 frozen±0.02 且 context +數百 token,支持「7B 上 prompt 層有天花板」;若 top5docs 逼近 cv-hybrid,則主 claim 需降級為「同效但零 context 成本」— 兩種結果都可發表,先寫進論文兩個版本的討論句。

---

## 4. 論文表格規格(草稿檔已建好對應空表)

- **Table 1 主結果**(24 全量 + clean-20 雙報):gold-rec / full-set / 首版覆蓋 / 六維 / off-srv / p 值 — 既有數字已填,top5docs、icl2 兩列 ⟨TBD⟩。
- **Table 2 成本表**:C1–C9 × 全臂 — Phase 0 即可全填(新臂除外)。
- **Table 3 文獻成本對照**(已填,全部原論文數字):card 3–5K tok/呼叫;RAG-MCP 1,084 vs 2,134;MCP-Zero 111 vs 6,308(−98%);ASA ~20KB 資產;cv ~100KB、sv 25K、zero context。
- **Table 4 穩健性**:4 子集重抽 0.864±0.005、G1b 自包含 0.863、held-out server 0.90–0.94、G0 p 值。
- **Figure:成本–效能前緣**(x=completion tokens/task,y=gold-recall;各臂一點,DEER 畫成 cv-hybrid 的可調曲線)— `lea_cost_metrics.py --pareto` 直接出 CSV。
```
