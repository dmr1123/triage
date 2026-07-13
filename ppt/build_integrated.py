# -*- coding: utf-8 -*-
"""完整整合版：把「報告摘要」與「詳細逐篇」整合進同一份 PPT。
第一部分＝報告摘要（總覽＋能力分層＋各總結）；第二部分＝5 篇逐篇詳解。"""
import sys
sys.path.insert(0, '/home/user/triage/ppt')
from deck_engine import new_deck, section_divider
import summary_slides as ss
from paper_content import (PAPERS, render_paper, render_compare, render_takeaways,
                           render_sources, render_references, render_glossary2, render_closing)

prs = new_deck()

# --------- 封面
ss.title_slide(prs, "低成本設備輔助檢傷（完整整合版）",
               ["報告摘要 ＋ 5 篇逐篇詳解 · 一份整合",
                "含「相機 / App / 便宜設備」能力分層"],
               "報告 + 詳細")

# --------- 第一部分：報告摘要
section_divider(prs, "第一部分", "報告摘要（快速看懂）",
                "共通主軸、能力分層（相機/App/便宜設備）、EHR 數據、相機能做什麼、主訴×EHR 整合方法", "1")
ss.summary_section(prs)   # overview_map, tiers, capability_matrix, ehr_data, camera_basic, camera_advanced, integration

# --------- 第二部分：詳細逐篇
section_divider(prs, "第二部分", "5 篇論文逐篇詳解",
                "每篇 6 頁：臨床問題與 dataset、設備與感測、完整流程圖、子模組訓練、結果與限制", "2")
for p in PAPERS:
    render_paper(prs, p)

# --------- 綜合 / 附錄
render_compare(prs)
render_takeaways(prs)
render_sources(prs)
render_references(prs)
render_glossary2(prs)
render_closing(prs)

OUT = '/home/user/triage/ppt/低成本設備輔助檢傷_完整整合版.pptx'
prs.save(OUT)
print("integrated deck saved:", len(prs.slides._sldIdLst), "slides ->", OUT)
