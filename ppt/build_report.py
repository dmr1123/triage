# -*- coding: utf-8 -*-
"""報告版（精簡）：每篇 2 頁，聚焦「訊號如何取得」＋「如何結合主訴做判斷」。
沿用 paper_content.PAPERS 的資料。"""
import sys
sys.path.insert(0, '/home/user/triage/ppt')
from deck_engine import *
from deck_engine import _blank
from paper_content import PAPERS
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = new_deck()


def _bullets(slide, l, t, w, items, size=12.5, gap=6, color=BODY, lh=1.2, h=Inches(4.2)):
    tf = textbox(slide, l, t, w, h)
    first = True
    for it in items:
        txt, lvl = (it if isinstance(it, tuple) else (it, 0))
        para(tf, txt, size - lvl, color if lvl == 0 else MUTED, bullet=True, level=lvl,
             space_after=gap, first=first, line_spacing=lh)
        first = False
    return tf


# 每篇的「結合主訴」重點 + 迷你融合流程 + 一句帶走（key = num）
REPORT = {
    "1": {
        "cc": "主訴以「結構化勾選清單」輸入（家長擔憂、呼吸困難，加觀察到的水腫、蒼白），"
              "和自動量到的生命徵象（年齡、心率、體溫、上臂圍、血氧）一起放進「同一條 Logistic 回歸公式」，"
              "各自是一個加權項，直接輸出一個住院風險機率，再用 8%／40% 兩個門檻分成紅／黃／綠。",
        "point": "重點：症狀與數字不是分開評分，而是同一條公式裡的權重——把「家長覺得不對勁」也變成一個可計算的變數。",
        "mini": (["徵象 ＋ 主訴(勾選)", "Logistic 回歸(9 變數)", "住院風險 → 紅/黃/綠"], ["Logistic 回歸(9 變數)"]),
        "take": "把主訴當成公式裡的變數，和血氧、心率等一起加權，最直接的「結合」。",
    },
    "2": {
        "cc": "主訴以勾選清單輸入（頭痛／視力、胸痛／喘、出血＋腹痛）加病史（胎次、懷孕週數），"
              "和血壓、尿蛋白、探頭測到的 SpO₂ 一起丟進既有的 miniPIERS Logistic 模型，"
              "輸出「48 小時內發生嚴重併發症」的機率，再轉成紅綠燈式檢傷。",
        "point": "重點：血氧探頭補上一個關鍵徵象——研究顯示把 SpO₂ 加進 miniPIERS，抓到高危孕婦的敏感度由 ~33% 升到 ~50%。",
        "mini": (["徵象 ＋ 症狀(勾選)", "miniPIERS 回歸", "48h 危險機率 → 分級"], ["miniPIERS 回歸"]),
        "take": "沿用成熟風險模型，手機＋血氧計把它搬到床邊；主訴與 SpO₂ 都是模型輸入。",
    },
    "3": {
        "cc": "主訴以 App 自填問卷收集，和量到的體溫／血氧／心率／咳嗽音一起「加密上傳到醫師的網頁儀表板」，"
              "由醫師（人）看著數字＋症狀趨勢判斷誰在惡化——是「人來融合」，沒有自動模型。",
        "point": "重點：這是另一條路線——不做自動評分，把客觀數據送到醫師眼前，讓專業判斷取代電話追蹤。",
        "mini": (["徵象 ＋ 自填症狀", "醫師看儀表板", "人工檢傷 / 惡化標記"], []),
        "take": "融合由「人」完成：便宜設備負責把徵象與症狀變成醫師看得到的硬數據。",
    },
    "4": {
        "cc": "主訴是護理師打的「自由文字」。模型先把文字斷詞、轉成詞向量（embedding，讓意義相近的詞數字也相近），"
              "再和生命徵象數字一起餵進神經網路的共同層，由網路自己「學」出哪些字句代表危險，輸出重症機率。",
        "point": "重點：這是最典型的「文字＋數字」自動融合。加入主訴文字後，AUC 由 0.82 升到 0.85，遠勝傳統 ESI（0.67）。",
        "mini": (["生命徵象數字 ＋ 主訴文字", "神經網路融合", "24h 重症機率"], ["神經網路融合"]),
        "take": "不需人工整理症狀，讓深度學習直接讀懂主訴文字，是最靈活的結合方式。",
    },
    "5": {
        "cc": "本篇「不使用主訴」，只做純訊號 → 血氧。它是上游的「感測積木」：量到的 SpO₂（低於 90% 警示）"
              "本身就是一個徵象，可以接到像論文 1、4 那樣的「主訴＋徵象」融合模型裡，補上「連便宜手機都能量血氧」這一塊。",
        "point": "重點：這篇解決的是『怎麼用一支普通手機取得血氧』；把它產生的 SpO₂ 餵進前幾篇的融合模型，就能結合主訴。",
        "mini": (["手機相機 PPG", "CNN 估血氧", "SpO₂(<90% 警示)"], ["CNN 估血氧"]),
        "take": "本身不含主訴，但提供最便宜的血氧來源，可當作其他融合模型的輸入。",
    },
}


def _badges_row(slide, top, dev, w=Inches(2.82), h=Inches(0.72)):
    items = [
        ("任何手機都能用？", dev["any_phone"][0], dev["any_phone"][1]),
        ("需要 App？", dev["app"][0], dev["app"][1]),
        ("開源？", dev["oss"][0], dev["oss"][1]),
        ("成本 vs NT$5000", "低成本" if dev["cost_kind"] == "ok" else ("超過" if dev["cost_kind"] == "warn" else "不適用"), dev["cost_kind"]),
    ]
    x = Inches(0.78); gap = Inches(0.14)
    for lab, val, kind in items:
        badge(slide, x, top, lab, val, kind=kind, w=w, h=h)
        x += w + gap


def _sensing_rows(slide, x, y, w, sensing, area_h=Inches(2.7)):
    n = len(sensing)
    two_col = n > 4
    if two_col:
        cols = 2
        per_col = (n + 1) // 2
        col_w = (w - Inches(0.35)) / 2
    else:
        cols = 1
        per_col = n
        col_w = w
    per_h = min(Inches(0.82), int(area_h / max(1, per_col)))
    fs = 11.5 if not two_col else 10.5
    for i, (sign, how) in enumerate(sensing):
        col = i // per_col
        row = i % per_col
        cx = x + col * (col_w + Inches(0.35))
        cy = y + row * per_h
        rect(slide, cx, cy + Inches(0.06), Inches(0.14), Inches(0.14), fill=ACCENT, shape=MSO_SHAPE.OVAL)
        tf = textbox(slide, cx + Inches(0.28), cy - Inches(0.02), col_w - Inches(0.32), per_h)
        para(tf, [(sign + "：", True, INK), (how, False, BODY)], fs, first=True, line_spacing=1.1)


def render_report_paper(prs, p):
    r = REPORT[p["num"]]
    # ---------------- Slide 1: 訊號如何取得
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    rect(s, 0, 0, SW, Inches(1.35), fill=PRIMARY)
    rect(s, 0, 0, Inches(0.22), Inches(1.35), fill=ACCENT)
    tf = textbox(s, Inches(0.78), Inches(0.2), Inches(9.8), Inches(1.05))
    para(tf, p["kicker"] + "　—　① 訊號如何取得", 11.5, RGBColor(0xBF, 0xDD, 0xE7), bold=True, space_after=3, first=True)
    para(tf, p["title"], 18, WHITE, bold=True, line_spacing=1.0)
    tfn = textbox(s, Inches(11.5), Inches(0.2), Inches(1.7), Inches(1.1))
    para(tfn, p["num"] + " / 5", 30, RGBColor(0x2A, 0x6A, 0x83), bold=True, align=PP_ALIGN.RIGHT, first=True)
    # badges
    _badges_row(s, Inches(1.55), p["device"])
    # device + cost line
    tf = textbox(s, Inches(0.78), Inches(2.42), Inches(11.75), Inches(0.85))
    para(tf, [("設備：", True, PRIMARY), (p["device"]["type"], False, BODY)], 11.5, first=True, line_spacing=1.12)
    para(tf, [("金額：", True, PRIMARY), (p["device"]["cost"], False, BODY)], 11.5, line_spacing=1.12, space_before=2)
    # sensing panel (focus)
    _, sx, sy, sw = panel_titled(s, Inches(0.78), Inches(3.45), Inches(11.75), Inches(3.35), "量到哪些徵象、訊號怎麼取得", accent=ACCENT, fill=RGBColor(0xED, 0xF6, 0xF8))
    _sensing_rows(s, sx, sy, sw, p["sensing"])
    footer(s)
    notes(s, "【訊號取得重點】\n" + "\n".join(f"· {sign}：{how}" for sign, how in p["sensing"]) +
          "\n\n設備：" + p["device"]["type"] + "\n金額：" + p["device"]["cost"])

    # ---------------- Slide 2: 如何結合主訴 → 判斷
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, p["kicker"], "② 如何結合主訴 → 做判斷", num=None)
    # cc panel
    _, cx, cy, cw = panel_titled(s, Inches(0.78), Inches(1.55), Inches(11.75), Inches(2.15), "主訴怎麼收集、怎麼和徵象結合")
    tf = textbox(s, cx, cy, cw, Inches(1.5))
    para(tf, r["cc"], 12.5, BODY, first=True, line_spacing=1.3)
    # mini fusion flow
    labels, models = r["mini"]
    flow_snake(s, Inches(1.4), Inches(4.05), Inches(10.5), labels, models, None, box_h=Inches(1.0), max_cols=3)
    # highlight + takeaway
    hk, hv, hd = p["hl"]
    hb = rect(s, Inches(0.78), Inches(5.5), Inches(3.0), Inches(1.25), fill=PRIMARY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.07)
    tf = textbox(s, Inches(0.92), Inches(5.6), Inches(2.72), Inches(1.05), anchor=MSO_ANCHOR.MIDDLE)
    para(tf, hk, 11, RGBColor(0xBF, 0xDD, 0xE7), bold=True, align=PP_ALIGN.CENTER, first=True, space_after=2)
    para(tf, hv, 24, WHITE, bold=True, align=PP_ALIGN.CENTER, space_after=2)
    para(tf, hd, 9.5, RGBColor(0xCF, 0xE2, 0xEA), align=PP_ALIGN.CENTER, line_spacing=1.0)
    callout(s, Inches(4.0), Inches(5.5), Inches(8.53), Inches(1.25), "一句帶走", r["point"] + "\n" + r["take"], accent=MODEL, fill=MODELBG)
    footer(s)
    notes(s, "【結合主訴】\n" + r["cc"] + "\n\n" + r["point"] + "\n" + r["take"])



def glossary_report(prs):
    """名詞速記：把報告後面會用到的術語先解釋清楚。"""
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "名詞速記", "先解釋術語——後面不再出現沒說明的縮寫", num=None)
    cols = [
        ("核心概念", PRIMARY, [
            ("檢傷 Triage", "人手不足時，快速決定「誰先看」。"),
            ("生命徵象", "心率·呼吸·血壓·體溫·血氧等基本讀數。"),
            ("主訴", "病人自己說哪裡不舒服（常一句話或勾選）。"),
            ("EHR 電子病歷", "存放病人資料的系統。"),
            ("篩檢級", "能初步過篩，但不取代正式檢驗。"),
            ("醫療級", "準確度接近正式醫療器材。"),
        ]),
        ("訊號與感測", ACCENT, [
            ("SpO₂ 血氧", "血液帶氧百分比，低於 90% 危險。"),
            ("PPG", "用光看血液脈動（忽亮忽暗＝心跳）。"),
            ("rPPG", "不碰身體、拍臉也能量的 PPG。"),
            ("OCR", "讓相機「讀」出螢幕上的數字。"),
            ("HRV 心率變異", "心跳間隔的變化，反映自律神經。"),
            ("MUAC 上臂圍", "量上臂一圈，看營養/病況。"),
        ]),
        ("AI 與模型", MODEL, [
            ("模型", "從資料學出規則：吃數字 → 吐預測。"),
            ("Logistic 回歸", "幾個輸入加權 → 算出 0~100% 機率。"),
            ("CNN", "擅長從影像/訊號抓特徵的神經網路。"),
            ("詞向量 embedding", "把文字變數字，讓模型讀懂主訴。"),
            ("AUC", "模型排序準不準：0.5 瞎猜～1 完美。"),
            ("ESI", "美國急診 5 級檢傷量表（傳統基準）。"),
        ]),
    ]
    xs = [Inches(0.78), Inches(4.68), Inches(8.58)]
    cw = Inches(3.7)
    for ci, (htitle, hcolor, terms) in enumerate(cols):
        x = xs[ci]
        hb = rect(s, x, Inches(1.6), cw, Inches(0.44), fill=hcolor, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
        htf = hb.text_frame; htf.vertical_anchor = MSO_ANCHOR.MIDDLE; htf.margin_left = Inches(0.12)
        para(htf, htitle, 12.5, WHITE, bold=True, first=True)
        for ti, (term, defn) in enumerate(terms):
            y = Inches(2.18) + ti * Inches(0.76)
            rect(s, x, y, cw, Inches(0.68), fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
            rect(s, x, y, Inches(0.07), Inches(0.68), fill=hcolor)
            tf = textbox(s, x + Inches(0.2), y + Inches(0.08), cw - Inches(0.3), Inches(0.56))
            para(tf, term, 11, PRIMARY, bold=True, space_after=1, first=True, line_spacing=1.0)
            para(tf, defn, 9.3, BODY, line_spacing=1.06)
    callout(s, Inches(0.78), Inches(6.82), Inches(11.75), Inches(0.42), "",
            "其他縮寫：CRT=微血管回填時間　·　PLR=瞳孔光反射　·　miniPIERS=一個孕婦風險模型　·　ratio-of-ratios=血氧計的比值算法。",
            accent=PRIMARY, fill=PANEL)


def _pill_right(slide, right_x, y, text, color):
    w = Inches(est_text_w_in(text, 10) + 0.36)
    sp = rect(slide, right_x - w, y, w, Inches(0.34), fill=color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = sp.text_frame; tf.word_wrap = False
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, text, 10, WHITE, bold=True, align=PP_ALIGN.CENTER, first=True)


def ai_papers_slide(prs, section_label, rows, repos_note=None, subtitle=None):
    """每個方法 → 代表『結合 AI』論文，附查證等級。"""
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "能力分層 · 代表 AI 論文", section_label, num=None)
    tfi = textbox(s, Inches(0.78), Inches(1.28), Inches(11.75), Inches(0.55))
    para(tfi, subtitle or "查證：已見原文＝在 GitHub 看到 arXiv 原始碼/作者程式碼；搜尋佐證＝論文真實、AI 用途有原頁引文，"
              "但全文 PDF 因本環境網路政策(egress)被擋、無法下載。", 9.5, MUTED, first=True, line_spacing=1.18)
    y0 = Inches(1.86); rh = Inches(0.585)
    for i, (method, ai, paper, vtext, vcolor) in enumerate(rows):
        y = y0 + i * rh
        rect(s, Inches(0.78), y, Inches(11.75), Inches(0.5), fill=(PANEL if i % 2 else RGBColor(0xEA, 0xF2, 0xF6)), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.09)
        rect(s, Inches(0.78), y, Inches(0.09), Inches(0.5), fill=vcolor)
        tfn = textbox(s, Inches(1.0), y + Inches(0.04), Inches(3.0), Inches(0.44), anchor=MSO_ANCHOR.MIDDLE)
        para(tfn, method, 11, INK, bold=True, space_after=0, first=True, line_spacing=1.0)
        para(tfn, ai, 8.5, MUTED, line_spacing=1.0)
        tfp = textbox(s, Inches(4.1), y + Inches(0.04), Inches(5.9), Inches(0.44), anchor=MSO_ANCHOR.MIDDLE)
        para(tfp, paper, 10, PRIMARY, bold=True, first=True, line_spacing=1.05)
        _pill_right(s, Inches(12.42), y + Inches(0.08), vtext, vcolor)
    if repos_note:
        callout(s, Inches(0.78), Inches(6.05), Inches(11.75), Inches(1.05), "已見原文的程式碼來源（GitHub 可存取）",
                repos_note, accent=GREEN, fill=RGBColor(0xEC, 0xF6, 0xF0))
    else:
        footer(s)


# ================================================================= FRONT + SUMMARY (shared)
import summary_slides as ss
ss.title_slide(prs, "低成本設備輔助檢傷（報告版）",
               ["聚焦：訊號如何取得 × 如何結合主訴做判斷",
                "並統整「相機 / App / 便宜設備」能測到哪些數值"],
               "5 篇論文 · 每篇 2 頁")
glossary_report(prs)       # 名詞速記：先把術語解釋清楚（放最前面）
ss.overview_map(prs)       # 總覽
ss.tiers(prs)              # 能力分層 Lv1 相機 / Lv2 App / Lv3 便宜設備
# 只列「100% 已查證原文（在 GitHub 看到作者原始碼/程式碼）」的方法
_AI_CONFIRMED = [
    ("Lv1 心率（指尖 PPG）", "conv＋LSTM 回歸心率", "Samavati 2022, arXiv:2204.08989（MEDVSE）", "已見原文", GREEN),
    ("Lv1 血氧 SpO₂（相機）", "CNN 估血氧", "Hoffman 2022, npj Digit Med 5:146", "已見原文", GREEN),
    ("Lv1 非接觸 rPPG（臉→心率/呼吸）", "深度卷積＋注意力", "Chen & McDuff 2018, ECCV（DeepPhys）", "已見原文", GREEN),
    ("Lv2 主訴文字（＋生命徵象）", "神經網路融合詞向量＋徵象", "Joseph 2020, JACEP Open 1(5):773", "已見原文", GREEN),
    ("Lv3 單導程 ECG → 心律不整", "34 層 CNN 分 12 種心律", "Hannun 2019, Nature Medicine 25:65", "已見原文", GREEN),
    ("Lv3 Cuffless 血壓（PPG）", "DNN 由 PPG 估血壓", "Hsu 2020, Sensors 20(19):5668", "已見原文", GREEN),
    ("Lv3 穿戴 PPG → 惡化預測", "Transformer 預測 2h 後惡化", "Ming 2024, npj Digit Med（登革熱）", "已見原文", GREEN),
]
_REPO_CONFIRMED = ("MEDVSE：github.com/MahdiFarvardin/MEDVSE　·　Hoffman：github.com/ubicomplab/oximetry-phone-cam-data　·　"
                   "DeepPhys：github.com/ubicomplab/rPPG-Toolbox　·　Joseph：github.com/jwjoseph/NN_triage_predict　·　"
                   "Hannun：github.com/awni/ecg（官方）　·　Hsu：github.com/Yan-Cheng-Hsu/Blood-Pressure-Estimation-Model（官方）　·　"
                   "Ming：github.com/jsmdaniels/VITAL（官方）")
_AI_SUBTITLE = ("只保留能在 GitHub 看到「作者原始碼／程式碼」、100% 確認用 AI 的方法（皆標「已見原文」）。"
                "其餘（心房顫動、貧血、黃疸、瞳孔、咳嗽、微血管回填、血糖、步態、呼吸音）因無法 100% 確認原文，暫不列入，待全文可存取再補。")
ai_papers_slide(prs, "僅列 100% 已查證原文者", _AI_CONFIRMED, repos_note=_REPO_CONFIRMED, subtitle=_AI_SUBTITLE)
ss.capability_matrix(prs)  # 能力對照表
ss.ehr_data(prs)
ss.camera_basic(prs)
ss.camera_advanced(prs)
ss.integration(prs)

# ================================================================= PAPERS
for p in PAPERS:
    render_report_paper(prs, p)

# ================================================================= CLOSING SUMMARY
s = _blank(prs)
rect(s, 0, 0, SW, SH, fill=BG)
title_bar(s, "小結", "兩種「結合主訴」的路線", num=None)
_, ax, ay, aw = panel_titled(s, Inches(0.78), Inches(1.6), Inches(5.75), Inches(4.4), "A. 自動融合（模型）", accent=MODEL, fill=MODELBG)
_bullets(s, ax, ay, aw, [
    "把徵象數字＋主訴一起餵給模型，直接輸出風險/分級",
    "論文 1 Smart Triage：勾選症狀＋SpO₂ 進 Logistic",
    "論文 2 PIERS：症狀＋SpO₂ 進 miniPIERS",
    "論文 4 Joseph：主訴『自由文字』進神經網路（最靈活）",
    "論文 5 Hoffman：提供便宜 SpO₂，可當上游輸入",
], size=12, gap=9)
_, bx, by, bw = panel_titled(s, Inches(6.78), Inches(1.6), Inches(5.75), Inches(4.4), "B. 人工融合（醫師）", accent=ACCENT)
_bullets(s, bx, by, bw, [
    "便宜設備只負責把徵象＋症狀變成客觀數據",
    "上傳儀表板，由醫師看趨勢判斷惡化",
    "論文 3 e-CoVig 走這條路",
    "優點：不需訓練資料、可解釋；缺點：仍要人力",
], size=12, gap=9)
callout(s, Inches(0.78), Inches(6.2), Inches(11.75), Inches(0.62), "",
        "訊號取得越便宜（手機相機/麥克風/外掛），就越能把「量徵象＋聽主訴」下放到第一線，補上沒有專業設備的缺口。", accent=PRIMARY, fill=PANEL)
footer(s)

OUT = '/home/user/triage/ppt/低成本設備輔助檢傷_報告版.pptx'
prs.save(OUT)
print("report deck saved:", len(prs.slides._sldIdLst), "slides ->", OUT)
