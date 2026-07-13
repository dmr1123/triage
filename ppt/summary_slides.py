# -*- coding: utf-8 -*-
"""Reusable overview / summary slides shared by the report and integrated decks.
Includes the tiered capability slides (Lv1 camera / Lv2 app / Lv3 cheap device)."""
from deck_engine import *
from deck_engine import _blank
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

EAF = RGBColor(0xEA, 0xF2, 0xF6)


def _bullets(slide, l, t, w, items, size=12.5, gap=6, color=BODY, lh=1.2, h=Inches(4.2)):
    tf = textbox(slide, l, t, w, h)
    first = True
    for it in items:
        txt, lvl = (it if isinstance(it, tuple) else (it, 0))
        para(tf, txt, size - lvl, color if lvl == 0 else MUTED, bullet=True, level=lvl,
             space_after=gap, first=first, line_spacing=lh)
        first = False
    return tf


def _mat_pill(slide, right_x, y, text, color, h=Inches(0.36)):
    w = Inches(est_text_w_in(text, 10.5) + 0.42)
    sp = rect(slide, right_x - w, y, w, h, fill=color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = sp.text_frame; tf.word_wrap = False
    tf.margin_left = 0; tf.margin_right = 0; tf.margin_top = 0; tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    para(tf, text, 10.5, WHITE, bold=True, align=PP_ALIGN.CENTER, first=True)


def title_slide(prs, main, sub_lines, tag):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=PRIMD)
    rect(s, 0, 0, Inches(0.24), SH, fill=ACCENT)
    tf = textbox(s, Inches(0.95), Inches(1.95), Inches(11.2), Inches(2.9))
    para(tf, main, 38, WHITE, bold=True, space_after=10, first=True, line_spacing=1.05)
    for i, ln in enumerate(sub_lines):
        para(tf, ln, 18, RGBColor(0xCF, 0xE2, 0xEA), space_after=2, line_spacing=1.2, first=False)
    tf2 = textbox(s, Inches(0.95), Inches(5.25), Inches(11), Inches(1))
    para(tf2, tag, 15, ACCENT, bold=True, first=True)
    return s


def overview_map(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "總覽", "共通主軸：取得訊號 → 結合主訴 → 判斷", num=None)
    flow_snake(s, Inches(1.4), Inches(1.7), Inches(10.5),
               ["便宜設備取得徵象", "結合主訴/症狀", "判斷（模型或醫師）"],
               ["判斷（模型或醫師）"],
               {"便宜設備取得徵象": "手機相機·血氧計·麥克風·外掛", "結合主訴/症狀": "自由文字 或 勾選清單", "判斷（模型或醫師）": "檢傷等級·風險機率"},
               box_h=Inches(1.05), max_cols=3)
    headers = ["#　論文", "訊號怎麼取得", "主訴怎麼結合"]
    col_w = [Inches(2.35), Inches(4.7), Inches(4.7)]
    rows = [
        ["1　Smart Triage", "夾式血氧計讀 SpO₂/心率＋人工量測", "勾選症狀與徵象同進 Logistic 公式"],
        ["2　PIERS", "手機接血氧探頭讀 SpO₂＋手動輸入", "症狀勾選＋SpO₂ 進 miniPIERS 模型"],
        ["3　e-CoVig", "DIY 外掛/相機測體溫·血氧·咳嗽音", "自填症狀＋數據上傳，醫師人工判"],
        ["4　Joseph", "沿用急診既有生命徵象數字", "主訴自由文字→詞向量，神經網路融合"],
        ["5　Hoffman", "手指按相機＋閃光→PPG→CNN 估血氧", "本篇不用主訴；SpO₂ 可接入他人模型"],
    ]
    simple_table(s, Inches(0.78), Inches(3.35), col_w, headers, rows, row_h=Inches(0.62), fs=11)
    footer(s)


def tiers(prs):
    """Lv1 camera / Lv2 app / Lv3 cheap-device — cumulative capability tiers."""
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "能力分層 · 總覽", "只用相機 → 加 App → 加便宜設備，各能測到什麼", num=None)
    tfi = textbox(s, Inches(0.78), Inches(1.3), Inches(11.75), Inches(0.35))
    para(tfi, "累加關係：每一層都包含前一層的能力，往下再多加。", 10.5, MUTED, first=True)
    data = [
        ("Lv1　只用相機（＋閃光）", ACCENT, "成本 $0 · 任何手機 · 代表：論文 5",
         "心率、血氧(篩檢)、呼吸；心房顫動、心率變異；OCR 讀既有裝置螢幕；"
         "影像篩檢：貧血·黃疸·微血管回填·瞳孔·非接觸臉部 rPPG。　（測不到體溫、血壓）"),
        ("Lv2　＋ App（麥克風·觸控·動作，仍無外接）", PRIMARY, "成本 $0 · 純軟體 · 代表：論文 1·3·4",
         "在 Lv1 之上再加：咳嗽/呼吸音(麥克風)、呼吸速率(點按 RRate)、"
         "動作/步態(加速度計)，以及症狀自填 / 主訴輸入（← 讓「結合主訴」成真）。"),
        ("Lv3　＋ 便宜外接設備（< NT$5000）", MODEL, "成本 數十~數百美元 · 代表：論文 1·2·3",
         "在 Lv2 之上再加：血氧/心率(醫療級·準，夾式血氧計)、體溫(紅外線計)、血壓(壓脈帶)、"
         "單導程心電圖(貼片)、尿蛋白/血糖(試紙)、上臂圍(量尺)。"),
    ]
    y = Inches(1.75); bh = Inches(1.62); gap = Inches(0.12)
    for i, (name, color, meta, caps) in enumerate(data):
        yy = y + i * (bh + gap)
        rect(s, Inches(0.78), yy, Inches(11.75), bh, fill=(EAF if i == 0 else PANEL), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
        rect(s, Inches(0.78), yy, Inches(0.13), bh, fill=color)
        # left label block
        tfn = textbox(s, Inches(1.05), yy + Inches(0.16), Inches(3.15), bh - Inches(0.3))
        para(tfn, name, 13.5, color, bold=True, space_after=5, first=True, line_spacing=1.05)
        para(tfn, meta, 9.5, MUTED, line_spacing=1.12)
        # right capabilities
        tfc = textbox(s, Inches(4.4), yy + Inches(0.18), Inches(8.05), bh - Inches(0.32), anchor=MSO_ANCHOR.MIDDLE)
        para(tfc, caps, 11.5, BODY, first=True, line_spacing=1.24)
    footer(s)


def capability_matrix(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "能力分層 · 對照表", "哪個數值，從哪一層開始能測？", num=None)
    headers = ["數值 / EHR", "Lv1　只相機", "Lv2　＋App（麥克風·觸控）", "Lv3　＋便宜外接設備"]
    col_w = [Inches(3.05), Inches(2.5), Inches(3.4), Inches(2.8)]
    rows = [
        ["心率 HR", "篩檢（接觸 PPG）", "篩檢", "可靠（血氧計）"],
        ["血氧 SpO₂", "篩檢（相機＋閃光）", "篩檢", "可靠（夾式血氧計）"],
        ["呼吸速率 RR", "概略（PPG/胸部）", "可（點按·麥克風）", "可"],
        ["體溫", "只能 OCR 讀", "只能 OCR 讀", "可靠（紅外線計）"],
        ["血壓 BP", "—", "—", "可（壓脈帶）"],
        ["心電圖 ECG", "—", "—", "可（單導程貼片）"],
        ["心房顫動 / 心律不整", "篩檢（PPG）", "篩檢", "可（ECG 更準）"],
        ["咳嗽 / 呼吸音", "—", "可（麥克風）", "可"],
        ["症狀 / 主訴", "—", "可（觸控輸入）", "可"],
        ["影像篩檢：貧血·黃疸·CRT·瞳孔·HRV", "可（影像）", "可", "可"],
        ["尿蛋白 / 血糖", "—", "—", "可（試紙）"],
    ]
    simple_table(s, Inches(0.78), Inches(1.62), col_w, headers, rows, row_h=Inches(0.42), fs=10, hfs=10.5, header_h=Inches(0.44))
    callout(s, Inches(0.78), Inches(6.72), Inches(11.75), Inches(0.4), "",
            "「—」= 該層做不到　·　「篩檢」= 篩檢級、不取代正式檢驗　·　「可靠」= 接近醫療級。體溫/血壓/心電圖幾乎都要到 Lv3。",
            accent=PRIMARY, fill=PANEL)
    footer(s)


def ehr_data(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "總結 · EHR 數據", "便宜設備現在能取得哪些 EHR 數據？", num=None)
    tfi = textbox(s, Inches(0.78), Inches(1.32), Inches(11.75), Inches(0.4))
    para(tfi, "每列＝ EHR 項目 ｜ 便宜取得方式 ｜ 出現於哪幾篇 ｜ 成熟度（綠=可靠　黃=篩檢/研究　紅=受限）", 10.5, MUTED, first=True)
    ehr = [
        ("心率 HR", "手機相機 PPG · 夾式血氧計 · 智慧手錶", "論文 1·2·3·5", "成熟", GREEN),
        ("血氧 SpO₂", "夾式/插入式血氧計(準) · 手機相機＋閃光(篩檢級)", "論文 1·2·3·5", "成熟 / 篩檢", GREEN),
        ("呼吸速率 RR", "App 點按(RRate) · 相機拍胸部起伏 · 麥克風", "論文 1", "尚可用", AMBER),
        ("體溫", "紅外線體溫計外掛 · 相機 OCR 讀顯示", "論文 1·3", "成熟", GREEN),
        ("血壓 BP", "壓脈帶手動輸入；純手機量測尚不可靠", "論文 2", "受限", RED),
        ("咳嗽 / 呼吸音", "手機麥克風錄音（自動分類仍研究）", "論文 3", "研究中", AMBER),
        ("臨床觀察（水腫·蒼白·意識）", "由醫護觀察後輸入 EHR 欄位", "論文 1·2", "靠人判讀", ACCENT),
    ]
    y0 = Inches(1.86); rh = Inches(0.64)
    for i, (name, method, papers, mat, color) in enumerate(ehr):
        y = y0 + i * rh
        rect(s, Inches(0.78), y, Inches(11.75), Inches(0.54), fill=(PANEL if i % 2 else EAF), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
        rect(s, Inches(0.78), y, Inches(0.09), Inches(0.54), fill=color)
        tfn = textbox(s, Inches(1.0), y + Inches(0.05), Inches(2.95), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfn, name, 12, INK, bold=True, first=True, line_spacing=1.0)
        tfm = textbox(s, Inches(4.0), y + Inches(0.05), Inches(4.9), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfm, method, 10.5, BODY, first=True, line_spacing=1.0)
        tfp = textbox(s, Inches(8.98), y + Inches(0.05), Inches(1.95), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfp, papers, 10.5, ACCENT, bold=True, first=True, line_spacing=1.0)
        _mat_pill(s, Inches(12.42), y + Inches(0.09), mat, color)
    callout(s, Inches(0.78), Inches(6.42), Inches(11.75), Inches(0.6), "",
            "註：論文 4（Joseph）不新增感測，直接沿用 EHR 既有生命徵象數字；上表列的是「用便宜設備主動取得」的對應。"
            "真正穩定 <NT$5000 的以心率、血氧、體溫、呼吸為主，血壓與聲音類仍是弱點。", accent=PRIMARY, fill=PANEL)


def camera_basic(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "聚焦相機 · 基本", "只用手機相機（含閃光），能做到哪些？", num=None)
    tfi = textbox(s, Inches(0.78), Inches(1.32), Inches(11.75), Inches(0.4))
    para(tfi, "純相機、不外接任何硬體能做的。狀態：綠=可靠　黃=篩檢/研究　紅=做不到/實驗", 10.5, MUTED, first=True)
    cam = [
        ("心率 HR", "手指蓋後鏡頭＋閃光 → 接觸式 PPG（血液脈動亮暗）", "論文 3·5", "可靠", GREEN),
        ("血氧 SpO₂", "同段指尖影片，比紅/藍綠光脈動比值 → CNN 估算", "論文 5", "篩檢級", AMBER),
        ("讀螢幕數字（OCR）", "拍血氧計/體溫計螢幕 → OCR 讀數字（間接）", "論文 3", "間接·成熟", GREEN),
        ("呼吸速率 RR", "指尖 PPG 基線起伏，或前鏡頭拍胸部起伏", "一般方法", "可行·研究", AMBER),
        ("體溫", "相機測不到熱 → 不能直測，只能 OCR 讀體溫計", "論文 3 (OCR)", "不能直測", RED),
        ("血壓 BP", "PPG 波形估血壓仍實驗、不可靠、非臨床級", "非這 5 篇", "實驗", RED),
        ("咳嗽 / 呼吸音", "屬手機「麥克風」，不是相機的工作", "—", "非相機", MUTED),
    ]
    y0 = Inches(1.86); rh = Inches(0.64)
    for i, (name, how, papers, st, color) in enumerate(cam):
        y = y0 + i * rh
        rect(s, Inches(0.78), y, Inches(11.75), Inches(0.54), fill=(PANEL if i % 2 else EAF), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
        rect(s, Inches(0.78), y, Inches(0.09), Inches(0.54), fill=color)
        tfn = textbox(s, Inches(1.0), y + Inches(0.05), Inches(2.85), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfn, name, 12, INK, bold=True, first=True, line_spacing=1.0)
        tfm = textbox(s, Inches(3.9), y + Inches(0.05), Inches(5.0), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfm, how, 10.5, BODY, first=True, line_spacing=1.0)
        tfp = textbox(s, Inches(8.98), y + Inches(0.05), Inches(1.95), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfp, papers, 10.5, ACCENT, bold=True, first=True, line_spacing=1.0)
        _mat_pill(s, Inches(12.42), y + Inches(0.09), st, color)
    callout(s, Inches(0.78), Inches(6.34), Inches(11.75), Inches(0.66), "核心",
            "相機其實只做兩件事：① 當「接觸式血氧感測器」（指尖 PPG → 心率可靠、血氧篩檢級）；② 當「掃描器」（OCR 讀既有裝置螢幕）。體溫、血壓相機都做不好。",
            accent=MODEL, fill=MODELBG)


def camera_advanced(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "聚焦相機 · 進階", "手機相機還能「篩檢」出這些（超出這 5 篇的研究）", num=None)
    tfi = textbox(s, Inches(0.78), Inches(1.32), Inches(11.75), Inches(0.4))
    para(tfi, "以下多來自這 5 篇以外的相機健康量測文獻，屬篩檢/研究級。狀態：綠=較成熟　黃=篩檢/研究　紅=實驗", 10.5, MUTED, first=True)
    more = [
        ("心房顫動 / 心律不整", "手指 PPG 脈搏不規則 → 偵測", "統合 敏感94%/特異96%", "篩檢級", GREEN),
        ("心率變異 HRV", "PPG 逐拍間隔 → 自律神經/壓力", "接觸 或 臉部 rPPG", "可行", AMBER),
        ("貧血 / 血紅素 Hb", "眼結膜 或 指甲床影像 → 估 Hb", "結膜~75%；HemaApp", "篩檢/研究", AMBER),
        ("黃疸 / 膽紅素（新生兒）", "皮膚 或 鞏膜影像 → 估膽紅素", "BiliCam R.84–.91、BiliScreen", "篩檢", AMBER),
        ("微血管回填 CRT", "指壓後短影片 → 自動測回填時間", "Cap App；敗血症檢傷", "新興", AMBER),
        ("瞳孔光反射 PLR", "前鏡頭＋閃光拍瞳孔對光收縮", "PupilScreen；腦傷/中風", "研究", AMBER),
        ("非接觸臉部 rPPG", "環境光拍臉 → 心率/呼吸/HRV（免碰）", "HR 誤差~0.1–0.4 bpm", "HR 可靠", GREEN),
    ]
    y0 = Inches(1.86); rh = Inches(0.64)
    for i, (name, how, rep, st, color) in enumerate(more):
        y = y0 + i * rh
        rect(s, Inches(0.78), y, Inches(11.75), Inches(0.54), fill=(PANEL if i % 2 else EAF), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
        rect(s, Inches(0.78), y, Inches(0.09), Inches(0.54), fill=color)
        tfn = textbox(s, Inches(1.0), y + Inches(0.05), Inches(2.85), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfn, name, 11.5, INK, bold=True, first=True, line_spacing=1.0)
        tfm = textbox(s, Inches(3.9), y + Inches(0.05), Inches(4.35), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfm, how, 10.5, BODY, first=True, line_spacing=1.0)
        tfp = textbox(s, Inches(8.35), y + Inches(0.05), Inches(2.55), Inches(0.46), anchor=MSO_ANCHOR.MIDDLE)
        para(tfp, rep, 10, ACCENT, bold=True, first=True, line_spacing=1.0)
        _mat_pill(s, Inches(12.42), y + Inches(0.09), st, color)
    callout(s, Inches(0.78), Inches(6.42), Inches(11.75), Inches(0.62), "",
            "共同原理：都在分析影像的「顏色·脈動·形狀」。多屬篩檢/研究級、不取代正式檢驗；顏色類（血氧·貧血·黃疸）受膚色影響是共同限制。",
            accent=MODEL, fill=MODELBG)


def integration(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "總結 · 整合方法", "現在「主訴 × EHR」的整合方法", num=None)
    methods = [
        ("A. 統計 / 機器學習模型", MODEL,
         "把症狀編成 0/1，和 EHR 數字放進同一條公式加權計算。",
         "→ 論文 1 Smart Triage、論文 2 PIERS（logistic 回歸）",
         "優：簡單、可解釋　　缺：症狀需先設計成勾選項"),
        ("B. 深度學習讀「自由文字」", MODEL,
         "主訴文字→詞向量(embedding)→神經網路，與 EHR 數字融合。",
         "→ 論文 4 Joseph（加主訴 AUC 0.82→0.85）",
         "優：最靈活、免人工整理　　缺：黑盒、需大量資料"),
        ("C. 人工融合（醫師）", ACCENT,
         "EHR 數據＋症狀上傳儀表板，由醫師看趨勢判讀。",
         "→ 論文 3 e-CoVig",
         "優：免訓練資料、可解釋　　缺：仍要人力"),
        ("D. 規則 / 危險徵象清單（傳統）", MUTED,
         "用固定規則，如 WHO 危險徵象、ESI 分級。",
         "→ 論文 4 用 ESI 當對照；論文 1 勾選項源自 WHO 危險徵象",
         "優：透明、好推廣　　缺：較不準（ESI AUC≈0.67）"),
    ]
    for i, (title, accent, how, ex, pc) in enumerate(methods):
        col = i % 2; row = i // 2
        x = Inches(0.78) + col * Inches(6.0)
        y = Inches(1.65) + row * Inches(2.5)
        rect(s, x, y, Inches(5.75), Inches(2.3), fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
        rect(s, x, y, Inches(0.11), Inches(2.3), fill=accent)
        tf = textbox(s, x + Inches(0.3), y + Inches(0.18), Inches(5.25), Inches(2.0))
        para(tf, title, 14, PRIMARY, bold=True, space_after=6, first=True)
        para(tf, how, 11.5, BODY, space_after=6, line_spacing=1.16)
        para(tf, ex, 11, ACCENT, bold=True, space_after=5, line_spacing=1.12)
        para(tf, pc, 10.5, MUTED, line_spacing=1.12)
    callout(s, Inches(0.78), Inches(6.55), Inches(11.75), Inches(0.44), "",
            "四種方法可混用：多數系統用 A/B 自動算風險，或用 C 讓醫師把關；A、B 正是「把主訴變成模型輸入」。", accent=PRIMARY, fill=PANEL)


def summary_section(prs):
    """The full report/summary section, shared by both decks."""
    overview_map(prs)
    tiers(prs)
    capability_matrix(prs)
    ehr_data(prs)
    camera_basic(prs)
    camera_advanced(prs)
    integration(prs)
