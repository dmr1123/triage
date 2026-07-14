# 相機 → 心率/呼吸率(HR/RR) 快速上手

影片進、數值出。兩支腳本、兩種用途。血氧(SpO₂)先不做(見主對話說明:相機血氧只有篩檢級、無現成權重)。

---

## 1. `quick_hr_pyvhr.py` — 最快先看「心率行不行」
classical rPPG,**不用權重、不用訓練**。適合先驗證相機測 HR 在你的影片上可不可行。

```bash
pip install pyVHR        # 或 pip install pyvhr（會帶 mediapipe/numba/torch/opencv）
python quick_hr_pyvhr.py --video myclip.mp4
# → {'median_hr_bpm': 72.3, 'mean_hr_bpm': 71.8, 'n_windows': 25}
```
- 影片:正面臉、光線足、盡量別晃、≥15 秒。
- ⚠️ pyVHR 各版本 `run_on_video` 參數名可能不同;對不上就照 <https://github.com/phuselab/pyVHR> 調(腳本內已標)。

---

## 2. `infer_rppg.py` — 用 rPPG-Toolbox 的 pretrained 深度模型出 HR(+近似 RR)
用官方 **TS-CAN** 權重估心率,並用呼吸基線調變估**近似**呼吸率。

```bash
# 準備(一次)
git clone https://github.com/ubicomplab/rPPG-Toolbox
cd rPPG-Toolbox
bash setup.sh conda && conda activate rppg-toolbox
ls final_model_release/          # 看有哪些 .pth（例如 PURE_TSCAN.pth）
cp /path/to/infer_rppg.py .      # 把本檔放到 repo 根目錄

# 執行(臉部影片)
python infer_rppg.py --video myclip.mp4 --weights final_model_release/PURE_TSCAN.pth --roi face
# 手指按鏡頭(指尖 PPG)：--roi full
# → {"hr_bpm": 72.4, "rr_bpm_approx": 15.2, "fps": 30.0, "frames_used": 600}
```

### ★★ 本機一定要核對的 3 件事(否則權重載不進去或形狀不符)
1. `--img_size` = 訓練該權重的 config `RESIZE`(標準 TSCAN 多為 **72**)。
2. `--frame_depth` = 該 config 的 `MODEL.TSCAN.FRAME_DEPTH`(常見 **10 或 20**)。
   → 去 `configs/` 找對應 YAML 看這兩個數字。
3. 權重檔名/路徑用 `ls final_model_release/` 確認。
若 `load_state_dict` 報 key/shape 不符,幾乎都是上面 1、2 沒對齊。

### 這支的 RR 是「近似值」
- HR:用官方 pretrained TS-CAN,**可信**。
- RR:用綠通道亮度的呼吸基線調變(FFT 0.1–0.5 Hz)估,**近似**、非深度模型。
- 想要研究級 RR → 改用官方 **BigSmall** 多任務模型(輸入/輸出較複雜),需要另寫 wrapper(可再找我)。

---

## 已驗 / 未驗(誠實標註)
| 項目 | 狀態 |
|---|---|
| 兩支腳本語法 | ✅ `py_compile` 通過 |
| HR/RR 的 FFT 數值抽取邏輯 | ✅ 用合成訊號單測:72bpm→72、15/min→15、混合訊號 RR 也抓對 |
| TS-CAN 權重實際載入 + 影片端到端 | ⚠️ **未跑**(此環境無 rPPG-Toolbox/權重/GPU) → 你本機第一次跑要照上面 3 點核對 |
| pyVHR 端到端 | ⚠️ 未跑(未裝 pyVHR) → 首次跑注意版本參數 |

## 常見狀況
- **心率明顯測不到**:影片太晃/太暗、臉太小、影片 <10 秒 → 換影片重試。
- **RR 亂跳**:呼吸訊號很弱,實驗室外常不穩;真實檢傷建議收一小批自有資料驗證。
- **要接進 triage 系統**:把輸出的 `{hr, rr}` 依你系統格式(REST/FHIR/表單)送進去即可。
