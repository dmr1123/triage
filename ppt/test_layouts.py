# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/user/triage/ppt')
from deck_engine import *
from deck_engine import _blank

prs = new_deck()

# ---- 1. TITLE
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=PRIMD)
rect(s, 0, 0, Inches(0.22), SH, fill=ACCENT)
tf = textbox(s, Inches(0.9), Inches(2.0), Inches(11.5), Inches(2.6))
para(tf, "低成本設備輔助檢傷", 40, WHITE, bold=True, space_after=6, first=True)
para(tf, "用手機與便宜裝置取得生命徵象，結合主訴做初步 triage / 急症判斷", 18, RGBColor(0xC9,0xDD,0xE6), space_after=0)
tf2 = textbox(s, Inches(0.9), Inches(5.3), Inches(11), Inches(1))
para(tf2, "5 篇論文導讀 · 給非醫療背景與 AI 初學者", 13, RGBColor(0xAF,0xC9,0xD6), first=True)

# ---- 2. OVERVIEW test with chips
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "總覽 Overview", "沒有專業設備時，大家用什麼做檢傷？", num=2)
x = Inches(0.78); y = Inches(1.6)
for label in ["手機相機 (PPG)", "夾式血氧計", "手機麥克風", "便宜穿戴裝置", "症狀 App"]:
    _, w = chip(s, x, y, label, fill=PANEL2, fg=PRIMARY, h=Inches(0.38))
    x += w + Inches(0.15)
# panel
p = rect(s, Inches(0.78), Inches(2.3), Inches(11.7), Inches(1.4), fill=PANEL,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
tf = p.text_frame; tf.margin_left=Inches(0.2); tf.margin_top=Inches(0.15)
para(tf, "通用配方", 13, PRIMARY, bold=True, first=True)
para(tf, [("量測生命徵象", True, INK), ("（心率、血氧、呼吸…） ＋ ", False, BODY),
          ("主訴 / 症狀", True, INK), ("（自由文字或勾選） → ", False, BODY),
          ("機器學習模型", True, MODEL), (" → 檢傷等級（紅 / 黃 / 綠）", False, BODY)], 13)
footer(s)

# ---- 3. PAPER HEADER test
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
rect(s, 0, 0, SW, Inches(2.05), fill=PRIMARY)
rect(s, 0, 0, Inches(0.22), Inches(2.05), fill=ACCENT)
tf = textbox(s, Inches(0.78), Inches(0.34), Inches(11.6), Inches(1.5))
para(tf, "論文 1 · 兒科快速檢傷", 12, RGBColor(0xBF,0xDD,0xE7), bold=True, first=True, space_after=3)
para(tf, "Smart Triage：低收入國家的兒童快速檢傷演算法", 22, WHITE, bold=True, line_spacing=1.0)
# meta chips row
x = Inches(0.78); y = Inches(2.25)
for t, c in [("引用數 ~45 (Scholar)", ACCENT), ("IF 2.6 (Front. Pediatr.)", PRIMARY), ("2022", MUTED)]:
    _, w = chip(s, x, y, t, fill=PANEL2, fg=c); x += w + Inches(0.15)
tf = textbox(s, Inches(0.78), Inches(2.85), Inches(11.7), Inches(0.7))
para(tf, "出處：Mawji A, et al. Smart triage: development of a rapid pediatric triage algorithm... Front Pediatr. 2022;10:976870.",
     10.5, MUTED, italic=True, first=True)
pnl = rect(s, Inches(0.78), Inches(3.7), Inches(11.7), Inches(2.9), fill=PANEL,
           shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
tf = pnl.text_frame; tf.margin_left=Inches(0.25); tf.margin_top=Inches(0.2); tf.word_wrap=True
para(tf, "這篇在做什麼？", 13, PRIMARY, bold=True, first=True, space_after=6)
para(tf, "在資源不足的醫院，護理人員用一台平板 App 加一個夾在手指上的便宜血氧計，"
        "把小朋友的症狀和量到的生命徵象輸入，模型就會把病童分成「緊急 / 優先 / 非緊急」三級，"
        "幫忙決定誰要先看。", 13, BODY, line_spacing=1.15)
footer(s)

# ---- 4. FLOW diagram test
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "論文 1 · 完整流程", "從症狀與血氧，到檢傷等級", num=4)
labels = ["蒐集症狀+危險徵象", "夾式血氧計量測", "資料整理成特徵", "XGBoost 風險模型", "算出風險分數", "分成紅/黃/綠三級"]
models = ["XGBoost 風險模型"]
details = {
    "蒐集症狀+危險徵象": "App 勾選咳嗽、呼吸困難等",
    "夾式血氧計量測": "血氧、心率、體溫",
    "資料整理成特徵": "轉成模型看得懂的數字",
    "XGBoost 風險模型": "9 個關鍵預測因子",
    "算出風險分數": "0–100% 危急機率",
    "分成紅/黃/綠三級": "決定看診先後",
}
flow_snake(s, Inches(0.78), Inches(1.75), Inches(11.7), labels, models, details)
footer(s)

# ---- 5. TABLE test
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "綜合比較", "五篇一次看懂", num=5)
headers = ["論文", "設備 / 金額", "生命徵象", "用主訴?", "檢傷輸出"]
col_w = [Inches(2.3), Inches(3.0), Inches(2.6), Inches(1.6), Inches(2.2)]
rows = [
    ["Smart Triage", "平板+夾式血氧計 / ~US$", "血氧,心率,體溫", "是(勾選)", "紅/黃/綠三級"],
    ["PIERS on Move", "手機+血氧探頭 / 低", "血氧,血壓", "是(症狀)", "子癇前症風險"],
    ["e-CoVig", "手機+自製外掛 / 低", "體溫,血氧,咳嗽", "是(自填)", "遠端監測分級"],
    ["Joseph 2020", "無(純資料) / —", "急診生命徵象", "是(文字)", "重症機率"],
    ["Hoffman 2022", "純手機相機 / US$0", "血氧(SpO2)", "否", "血氧估計值"],
]
simple_table(s, Inches(0.78), Inches(1.8), col_w, headers, rows, row_h=Inches(0.6))
footer(s)

out = '/home/user/triage/ppt/_test.pptx'
prs.save(out)
print("saved", out, "slides:", len(prs.slides._sldIdLst))
