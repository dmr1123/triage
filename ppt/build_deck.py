# -*- coding: utf-8 -*-
"""Build the full Traditional-Chinese slide deck:
低成本設備輔助檢傷 —— 5 篇論文導讀。Content authored in zh-TW, grounded in papers.json."""
import sys
sys.path.insert(0, '/home/user/triage/ppt')
from deck_engine import *
from deck_engine import _blank
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = new_deck()

def bullets(slide, l, t, w, items, size=12.5, gap=6, color=BODY, lh=1.16):
    tf = textbox(slide, l, t, w, Inches(4.5))
    first = True
    for it in items:
        if isinstance(it, tuple):
            txt, lvl = it
        else:
            txt, lvl = it, 0
        para(tf, txt, size - (lvl * 1.0), color if lvl == 0 else MUTED, bullet=True, level=lvl,
             space_after=gap, first=first, line_spacing=lh)
        first = False
    return tf

# ================================================================= 1 TITLE
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=PRIMD)
rect(s, 0, 0, Inches(0.24), SH, fill=ACCENT)
# subtle accent block
rect(s, Inches(9.6), 0, Inches(3.73), SH, fill=RGBColor(0x0D, 0x2C, 0x3B))
tf = textbox(s, Inches(0.95), Inches(1.9), Inches(9.2), Inches(2.9))
para(tf, "低成本設備輔助檢傷", 46, WHITE, bold=True, space_after=8, first=True)
para(tf, "用手機與便宜裝置取得生命徵象，結合主訴，", 19, RGBColor(0xCF, 0xE2, 0xEA), space_after=2, line_spacing=1.2)
para(tf, "做初步 triage（檢傷）與急症判斷", 19, RGBColor(0xCF, 0xE2, 0xEA), line_spacing=1.2)
tf2 = textbox(s, Inches(0.95), Inches(5.25), Inches(9), Inches(1.4))
para(tf2, "5 篇論文導讀", 16, ACCENT, bold=True, space_after=4, first=True)
para(tf2, "為「不懂醫療」與「AI 初學者」而寫 · 全程白話 + 名詞解釋", 12.5, RGBColor(0xA9, 0xC6, 0xD3))
# triage dots decoration
for i, c in enumerate([RED, AMBER, GREEN]):
    rect(s, Inches(10.75), Inches(2.15 + i*0.62), Inches(0.34), Inches(0.34),
         fill=c, shape=MSO_SHAPE.OVAL)
tfd = textbox(s, Inches(11.25), Inches(2.05), Inches(2), Inches(2))
for i, t in enumerate(["紅 · 緊急", "黃 · 優先", "綠 · 非緊急"]):
    para(tfd, t, 12, RGBColor(0xCF,0xE2,0xEA), space_before=(0 if i==0 else 9), first=(i==0))

# ================================================================= 2 AGENDA
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "導覽 · 這份簡報怎麼看", "從「大方向」到「一篇一篇拆解」", num=2)
# left: structure
_, cx, cy, cw = panel_titled(s, Inches(0.78), Inches(1.65), Inches(6.0), Inches(4.9), "簡報結構")
bullets(s, cx, cy, cw, [
    "① 總覽：沒有專業設備時，大家用哪些便宜方法做檢傷、通用「配方」長怎樣",
    "② 五篇逐篇拆解，每篇固定回答 4 件事：",
    ("在什麼資料（dataset）上訓練", 1),
    ("用什麼設備、推測多少錢、要不要 App、有沒有開源", 1),
    ("量哪些徵象、怎麼量（例：手指按相機測血氧）", 1),
    ("完整流程圖 + 各子模組訓練 + 各感測器介紹", 1),
    "③ 五篇綜合比較表 + 重點總結 + 名詞表",
], size=12.5, gap=7)
# right: how to read badges
_, dx, dy, dw = panel_titled(s, Inches(7.0), Inches(1.65), Inches(5.5), Inches(4.9), "看圖小抄", accent=ACCENT, fill=RGBColor(0xED,0xF6,0xF8))
# legend items
yy = Inches(2.35)
rect(s, dx, yy, Inches(0.5), Inches(0.34), fill=MODELBG, line=MODEL, line_w=1.4, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
tf = textbox(s, dx+Inches(0.7), yy-Inches(0.02), dw-Inches(0.8), Inches(0.5))
para(tf, [("橘框 = 需要「訓練」的 AI/統計模型", False, BODY)], 11.5, first=True)
yy = Inches(2.95)
rect(s, dx, yy, Inches(0.5), Inches(0.34), fill=PANEL, line=ACCENT, line_w=1.4, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
tf = textbox(s, dx+Inches(0.7), yy-Inches(0.02), dw-Inches(0.8), Inches(0.5))
para(tf, "藍框 = 一般步驟（量測、輸入、顯示）", 11.5, BODY, first=True)
yy = Inches(3.55)
for i,(c,lab) in enumerate([(GREEN,"綠 = 好消息 / 有支援"),(RED,"紅 = 沒有 / 限制"),(AMBER,"黃 = 要注意")]):
    rect(s, dx, yy+Inches(i*0.5), Inches(0.34), Inches(0.34), fill=c, shape=MSO_SHAPE.OVAL)
    tf = textbox(s, dx+Inches(0.55), yy+Inches(i*0.5)-Inches(0.02), dw-Inches(0.7), Inches(0.45))
    para(tf, lab, 11.5, BODY, first=True)
callout(s, dx-Inches(0.02), Inches(5.2), dw+Inches(0.1), Inches(1.05), "一句話",
        "「檢傷 / triage」= 在人手不足時，快速決定「誰要先看」。這 5 篇都在想辦法用便宜工具把這件事做得又快又準。", accent=PRIMARY, fill=WHITE)
footer(s)

# ================================================================= 3 GLOSSARY quickstart
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "開始前 · 名詞速記", "看懂後面所有內容，只需先記這 8 個詞", num=3)
terms = [
    ("檢傷 / Triage", "人手不足時，把病人依「有多急」分級、決定看診先後。"),
    ("生命徵象 / Vital signs", "身體的基本讀數：心率、呼吸、血壓、體溫、血氧。"),
    ("主訴 / Chief complaint", "病人自己說「哪裡不舒服」，常是一句話或勾選症狀。"),
    ("血氧 / SpO₂", "血液帶氧的百分比，正常約 95–100%，低於 90% 危險。"),
    ("PPG（光體積變化描記）", "用光看血液脈動：每次心跳血流變化會讓光忽亮忽暗。"),
    ("脈搏血氧計 / Pulse oximeter", "夾手指、用紅光+紅外光量血氧與心率的小裝置。"),
    ("模型 / ML model", "從大量資料「學」出規則的程式，吃進數字吐出預測。"),
    ("AUROC / AUC", "模型排序準不準的分數：0.5=瞎猜，1.0=完美。"),
]
col_w = Inches(5.85)
xs = [Inches(0.78), Inches(6.95)]
for i, (term, desc) in enumerate(terms):
    col = i // 4
    row = i % 4
    x = xs[col]
    y = Inches(1.7) + Inches(row * 1.28)
    sp = rect(s, x, y, col_w, Inches(1.12), fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    rect(s, x, y, Inches(0.09), Inches(1.12), fill=ACCENT)
    tf = textbox(s, x + Inches(0.28), y + Inches(0.13), col_w - Inches(0.45), Inches(0.9))
    para(tf, term, 13, PRIMARY, bold=True, space_after=3, first=True)
    para(tf, desc, 11, BODY, line_spacing=1.12)
footer(s)

# ================================================================= 4 OVERVIEW: problem
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "總覽 ① · 問題", "什麼叫「沒有專業設備的情境」？", num=4)
scenes = [
    ("🏥", "低收入國家診所", "病童擠爆門診、醫護太少，沒有昂貴監視器，卻要馬上分辨誰快不行了。"),
    ("🏠", "COVID 居家隔離", "大量輕症在家，只靠護理師打電話追蹤，看不到血氧等硬數據，會漏掉「無聲缺氧」。"),
    ("🚪", "急診檢傷檯", "病人一到，護理師幾秒內只拿到幾個生命徵象+一句主訴，就要判斷會不會變重症。"),
]
for i, (icon, t, d) in enumerate(scenes):
    x = Inches(0.78) + i * Inches(4.02)
    sp = rect(s, x, Inches(1.75), Inches(3.75), Inches(3.15), fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
    tf = textbox(s, x + Inches(0.28), Inches(2.0), Inches(3.2), Inches(2.7))
    para(tf, icon, 30, INK, space_after=6, first=True)
    para(tf, t, 15, PRIMARY, bold=True, space_after=8)
    para(tf, d, 12, BODY, line_spacing=1.2)
callout(s, Inches(0.78), Inches(5.2), Inches(11.75), Inches(1.15), "共同點",
        "都缺「昂貴專業設備」與「足夠人力」，但決定又必須「快」。→ 於是研究者想：能不能用大家口袋裡就有的手機、或幾百塊的小裝置，補上這一塊？", accent=MODEL, fill=MODELBG)
footer(s)

# ================================================================= 5 OVERVIEW: devices
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "總覽 ② · 便宜設備地圖", "沒有專業設備時，大家用這 5 類簡易工具", num=5)
devs = [
    ("📷 手機相機 (PPG)", "手指按住鏡頭+開閃光，相機拍血液脈動→算心率、甚至血氧。任何有相機的手機都行。", ACCENT),
    ("🔴 夾式/插入式血氧計", "真正的醫療級指夾探頭，插上手機或平板讀 SpO₂、心率。準，但要多帶一個小配件。", PRIMARY),
    ("🎤 手機麥克風", "錄咳嗽、呼吸音，之後給人或 AI 判斷。零成本、任何手機都有。", ACCENT),
    ("🔧 便宜微控制器外掛", "ESP32＋感測晶片（血氧、紅外線體溫）自製小裝置，材料成本幾百塊台幣。", MODEL),
    ("💾 純軟體（用既有資料）", "不加任何硬體，只用醫院既有的生命徵象+主訴文字，靠更聰明的模型榨出價值。", PRIMARY),
]
for i, (t, d, c) in enumerate(devs):
    row = i
    y = Inches(1.68) + row * Inches(0.98)
    sp = rect(s, Inches(0.78), y, Inches(11.75), Inches(0.86), fill=PANEL if i%2 else RGBColor(0xEA,0xF2,0xF6), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    rect(s, Inches(0.78), y, Inches(0.10), Inches(0.86), fill=c)
    tf = textbox(s, Inches(1.05), y + Inches(0.12), Inches(3.3), Inches(0.62), anchor=MSO_ANCHOR.MIDDLE)
    para(tf, t, 13.5, INK, bold=True, first=True, line_spacing=1.0)
    tf2 = textbox(s, Inches(4.5), y + Inches(0.1), Inches(7.9), Inches(0.66), anchor=MSO_ANCHOR.MIDDLE)
    para(tf2, d, 11.5, BODY, first=True, line_spacing=1.1)
footer(s)

# ================================================================= 6 OVERVIEW: recipe
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "總覽 ③ · 通用配方", "幾乎所有做法都是同一個公式", num=6)
# the recipe flow
rlabels = ["量生命徵象", "收集主訴/症狀", "融合", "檢傷等級"]
rmodels = ["融合"]
rdetails = {"量生命徵象":"心率·血氧·呼吸·體溫", "收集主訴/症狀":"自由文字或勾選清單", "融合":"模型自動 或 醫師判讀", "檢傷等級":"紅/黃/綠·危險機率"}
flow_snake(s, Inches(0.9), Inches(1.7), Inches(11.5), rlabels, rmodels, rdetails, box_h=Inches(1.0), max_cols=4)
# two fusion styles
_, ax, ay, aw = panel_titled(s, Inches(0.78), Inches(3.5), Inches(5.75), Inches(1.7), "「融合」有兩種", accent=MODEL, fill=MODELBG)
bullets(s, ax, ay, aw, [
    "A. 模型自動融合：把數字+主訴一起丟進 AI，直接吐出風險分（第 1、2、4、5 篇）",
    "B. 人來融合：資料上傳儀表板，讓醫師自己看著判斷（第 3 篇 e-CoVig）",
], size=11.5, gap=6)
_, bx, by, bw = panel_titled(s, Inches(6.78), Inches(3.5), Inches(5.75), Inches(1.7), "「便宜」到什麼程度？", accent=PRIMARY)
bullets(s, bx, by, bw, [
    "真的 <NT$5000：純手機相機、麥克風、ESP32 自製外掛、純軟體",
    "會超過：醫療級夾式血氧計+平板整套（Smart Triage 那類，數千～上萬）",
], size=11.5, gap=6)
callout(s, Inches(0.78), Inches(5.45), Inches(11.75), Inches(0.95), "重點",
        "「主訴」很關鍵：光有生命徵象數字常常不夠準；把病人「說哪裡不舒服」也放進模型，準確度會明顯提升（第 4 篇會用數字證明這件事）。", accent=ACCENT)
footer(s)

# ================================================================= 7 OVERVIEW: map of 5 papers
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "總覽 ④ · 五篇地圖", "這 5 篇分別站在什麼位置", num=7)
headers = ["#", "論文（簡稱）", "代表什麼", "設備型態", "主訴融合"]
col_w = [Inches(0.5), Inches(2.7), Inches(4.05), Inches(2.6), Inches(1.9)]
rows = [
    ["1", "Smart Triage", "最完整的「兒科檢傷系統」旗艦", "平板＋夾式血氧計", "有 · 模型"],
    ["2", "PIERS on the Move", "把手機＋血氧計帶到產科（孕婦）", "手機＋血氧探頭", "有 · 模型"],
    ["3", "e-CoVig", "自製便宜外掛＋多重感測（COVID）", "手機＋DIY外掛", "有 · 人工"],
    ["4", "Joseph 2020", "純軟體：AI 融合「主訴文字＋數字」", "無（純資料）", "有 · 深度學習"],
    ["5", "Hoffman 2022", "最純的「手指按相機測血氧」機制", "純手機相機", "無"],
]
simple_table(s, Inches(0.78), Inches(1.75), col_w, headers, rows, row_h=Inches(0.72), fs=11.5)
callout(s, Inches(0.78), Inches(6.05), Inches(11.75), Inches(0.72), "",
        "順序刻意從「完整系統」講到「最底層感測原理」：第 5 篇 Hoffman 正好解釋了前幾篇「手機怎麼量到血氧」的物理原理。", accent=PRIMARY, fill=PANEL)
footer(s)

# ================================================================= PAPERS
from paper_content import (PAPERS, render_paper, render_compare, render_takeaways,
                           render_sources, render_references, render_glossary2, render_closing)
for p in PAPERS:
    render_paper(prs, p)

# ================================================================= BACK MATTER
render_compare(prs)
render_takeaways(prs)
render_sources(prs)
render_references(prs)
render_glossary2(prs)
render_closing(prs)

OUT = '/home/user/triage/ppt/低成本設備輔助檢傷_5篇論文導讀.pptx'
prs.save(OUT)
print("FULL deck saved:", len(prs.slides._sldIdLst), "slides ->", OUT)
