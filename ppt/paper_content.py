# -*- coding: utf-8 -*-
"""Authored zh-TW content for the 5 papers + render_paper()/back matter.
Facts grounded in papers.json; wording rewritten for non-medical / AI-beginner readers."""
from deck_engine import *
from deck_engine import _blank
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def _bullets(slide, l, t, w, items, size=12, gap=6, color=BODY, lh=1.16, h=Inches(4.2)):
    tf = textbox(slide, l, t, w, h)
    first = True
    for it in items:
        txt, lvl = (it if isinstance(it, tuple) else (it, 0))
        para(tf, txt, size - lvl, color if lvl == 0 else MUTED, bullet=True, level=lvl,
             space_after=gap, first=first, line_spacing=lh)
        first = False
    return tf


PAPERS = [
    {
        "num": "1", "kicker": "論文 1 · 兒科快速檢傷（低收入國家）",
        "title": "Smart Triage：低收入國家的兒童快速檢傷演算法",
        "citation": "Mawji A, Li E, Dunsmuir D, et al. Smart triage: development of a rapid pediatric triage algorithm for use in low-and-middle income countries. Front Pediatr. 2022;10:976870.　＋外部驗證：Kigo J, et al. PLOS Digit Health. 2024;3(6):e0000293.",
        "cit": "引用數 約 40–90（估計）", "if": "IF ≈ 2.6–3.4（Front. Pediatr．Q1 兒科）", "year": "2022",
        "one": "一台平板＋一個夾手指的血氧計，護理師幾分鐘就能把病童分成紅／黃／綠三級，決定誰要先救。",
        "lay": "低收入國家的診所常擠滿生病的孩子，卻沒有足夠受過訓練的醫護，很難一眼看出哪個孩子病危。這團隊做了「Smart Triage」：一台平板 App 加一個夾在手指上的便宜血氧計。護理師在門口花幾分鐘，輸入幾個簡單事實（年齡、家長是否擔心、有沒有呼吸困難、水腫、蒼白）加上自動量到的生命徵象（心率、血氧、體溫、上臂圍），一條統計公式就把孩子分成紅（緊急）／黃（優先）／綠（非緊急）。用烏干達約 1,600 名兒童建立、再用肯亞約 5,000 名兒童測試，能可靠地標出後來真的需要住院的孩子（準確度分數約 0.82）。",
        "problem": "在低收入國家的門診／急診，大量生病的孩子湧入、醫護太少，很難快速看出誰已經病危（包含早期敗血症）。晚一步發現最重的孩子就可能致命。這個問題就是：給第一線人員一個「免大量訓練、又快又可靠」的方法，在進門第一關就把孩子分成『現在要救』和『可以安全等候』。",
        "dataset": [
            "訓練（開發）資料：烏干達 Jinja 轉診醫院，前瞻收案 1,612 名急性生病的 5 歲以下兒童",
            "預測標籤：是否「住院」——當作『病危／需緊急照護』的客觀替身；住院率約 23%",
            "用平板 App 當場收資料（非事後翻病歷）；資料非公開",
            "切分：80／20 訓練／測試 ＋ 10 折交叉驗證",
            "外部驗證：肯亞 2 家醫院共 5,003 名兒童（Kigo 2024）",
        ],
        "device": {
            "type": "平板（Samsung Galaxy A8）＋ Masimo iSpO₂ 夾式指尖血氧計；醫師端另有儀表板",
            "cost": "平板 ~US$200–250 ＋ 醫療級血氧計 ~US$200–300 → 整套約 NT$1.3–1.7 萬",
            "any_phone": ("不是隨便一台", "no"), "app": ("要（Android 專用 App）", "warn"),
            "oss": ("App 未開源", "no"), "cost_kind": "warn",
            "note": "這是「醫療級夾式血氧計」，不是幾百塊的小玩意；整套超過 NT$5000。可重用的是已發表的 9 變數 logistic 公式（可自行實作）。",
        },
        "sensing": [
            ("心率 HR", "Masimo iSpO₂ 指夾直接讀出"),
            ("血氧 SpO₂", "指夾用紅光＋紅外光穿過指尖，量含氧／缺氧血液吸光差 → 算血氧"),
            ("呼吸速率 RR", "App 內建 RRate：跟著孩子每次呼吸點一下螢幕，換算每分鐘呼吸數（註：最後模型沒用到）"),
            ("體溫", "體溫計量測，護理師輸入 App"),
            ("上臂圍 MUAC", "捲尺量上臂，反映營養狀態"),
            ("觀察徵象", "水腫、蒼白由護理師勾選（人為感測）"),
        ],
        "flow": (
            ["病童到檢傷檯", "護理師輸入症狀", "夾式血氧計量測", "量體溫·臂圍·呼吸",
             "算 9 項風險分數", "套用 8%·40% 門檻", "分成紅/黃/綠三級", "儀表板追蹤病人"],
            ["算 9 項風險分數"],
            {"病童到檢傷檯": "急性生病兒童＋家長到門診", "護理師輸入症狀": "勾選家長擔憂、呼吸困難、水腫、蒼白",
             "夾式血氧計量測": "自動讀 SpO₂、心率", "量體溫·臂圍·呼吸": "體溫計、MUAC 尺、RRate 點按",
             "算 9 項風險分數": "logistic 回歸算住院機率", "套用 8%·40% 門檻": "低切點顧敏感、高切點顧特異",
             "分成紅/黃/綠三級": "決定看診先後", "儀表板追蹤病人": "高風險排最前"}
        ),
        "submodules": [
            ("檢傷風險模型 ★核心", "多變數 Logistic 回歸（非 XGBoost）", "烏干達 1,612 童；bootstrap 逐步挑出 9 個預測因子", "9 項輸入 → 住院機率 0–1"),
            ("門檻切分規則", "資料調校（非學習模型）", "在資料上選 8%（~90% 敏感度）、40%（~90% 特異度）", "機率 → 紅/黃/綠"),
            ("RRate 呼吸估計", "節拍／訊號處理（非模型）", "另篇發表的方法", "點按節奏 → 呼吸/分"),
            ("SpO₂／HR 運算", "Masimo 硬體內建（廠商演算法）", "非本團隊訓練", "光訊號 → 血氧/心率"),
        ],
        "sub_note": "外部驗證（Kigo 2024）只重新校準模型的「截距」一個參數，就能用到肯亞。",
        "sensors": [
            ("Masimo iSpO₂ 指夾", "血氧＋心率", "紅／紅外光穿指尖，含氧與缺氧血吸光不同；分離出血液脈動 → 算 SpO₂ 與心率"),
            ("RRate（軟體感測）", "呼吸速率", "用觸控螢幕：每次呼吸點一下，把間隔換算成呼吸/分"),
            ("體溫計 ／ MUAC 量尺", "體溫 ／ 上臂圍", "標準量測後輸入 App"),
            ("護理師（人為感測）", "水腫·蒼白·呼吸困難·家長擔憂", "以勾選清單輸入"),
        ],
        "results": [
            "外部驗證 AUROC：醫院1 0.826、醫院2 0.784、合併 0.821 → 良好且可跨場域",
            "門檻設計：低切點顧敏感度(~90%)、高切點顧特異度(~90%)",
            "落地效果：肯亞「打上靜脈抗生素的時間」縮短約 57%",
        ],
        "limits": [
            "預測「住院」只是病危的替身，會受非臨床住院習慣影響",
            "單一醫院開發；換到肯亞需重新校準截距才準",
            "呼吸速率雖有收集卻沒進最終模型；體溫／MUAC 靠人工量測",
            "整套設備超過低成本(<US$155)門檻，也無法用任意手機跑",
        ],
        "hl": ("AUROC", "0.82", "外部驗證判別力"),
    },
    {
        "num": "2", "kicker": "論文 2 · 孕婦子癇前症檢傷",
        "title": "PIERS on the Move：子癇前症檢傷的手機 App",
        "citation": "Lim J, Cloete G, Dunsmuir DT, et al. Usability and feasibility of PIERS on the Move: an mHealth app for pre-eclampsia triage. JMIR Mhealth Uhealth. 2015;3(2):e37.　（模型來源：Payne BA, et al. miniPIERS. PLoS Med. 2014;11:e1001589.）",
        "cit": "引用數 約 60（Crossref 估計）", "if": "IF 5.4（JMIR mHealth uHealth，2024）", "year": "2015",
        "one": "手機插上一個血氧探頭，護理師照著問幾個症狀，就能算出孕婦 48 小時內出大事的機率。",
        "lay": "子癇前症（懷孕時血壓危險升高）在缺醫少藥的窮國奪走許多母親性命。研究者做了便宜的手機 App「PIERS on the Move」，護理師在床邊：問一串症狀清單、記血壓與尿液試紙、再用插在手機上的指夾探頭讀血氧。App 把這些送進既有的統計風險模型（miniPIERS），估出她 48 小時內發生嚴重併發症的機率並給出檢傷建議。在南非 37 位護理師/助產士測試中，改良後被評為好用；試點中一位護理師對 200+ 位孕婦做了 500+ 次評估、每次約 5 分鐘。本篇證明「可行、好用」，但沒有證明能改善結果。",
        "problem": "子癇前症是孕產婦死亡的主因，且多發生在醫師少、缺乏檢驗、離醫院遠的低收入地區。第一線護理師／助產士常難以分辨哪位高血壓孕婦即將病危（抽搐、器官衰竭），因此需要緊急轉診。這個便宜手機工具帶他們走完『問症狀 → 量測 → 算風險』，幫忙決定誰該轉診。對象是低資源地區、懷孕 20 週以上的高血壓孕婦。",
        "dataset": [
            "本篇是「好不好用 ＋ 可行性」研究，不是訓練模型的研究",
            "好用性：南非 37 位護理師／助產士做情境測試（含 Frere 醫院 22 位），兩輪迭代",
            "可行性：1 位研究護理師對 200+ 位孕婦做了 500+ 次評估，每次約 5 分鐘",
            "內建模型 miniPIERS 另外訓練：5 個低收入國家、2,081 位妊娠高血壓孕婦（Payne 2014）",
            "模型標籤：入院 48 小時內是否發生嚴重母體不良結局（死亡／重大器官併發症）",
        ],
        "device": {
            "type": "市售 Android 手機 ＋『Phone Oximeter』指夾血氧探頭（UBC 研發，早期經耳機孔連接）",
            "cost": "血氧探頭目標價 ~US$40 ＋ 中階 Android 手機 → 整套 < NT$5000",
            "any_phone": ("手機幾乎任一台可", "ok"), "app": ("要（Android 專用）", "warn"),
            "oss": ("未開源（研究／商用）", "no"), "cost_kind": "ok",
            "note": "血氧來自「真的血氧探頭」，不是手機相機。手機本身不需特殊硬體；但一定要外接這個探頭。",
        },
        "sensing": [
            ("血氧 SpO₂＋脈搏", "指夾探頭：紅／紅外光穿指尖，含氧/缺氧血吸光不同 → 算 SpO₂ 與心率，傳回 App"),
            ("血壓", "標準血壓計量測，手動輸入"),
            ("尿蛋白", "標準尿液試紙，選等級輸入"),
            ("症狀·病史", "以勾選清單輸入（見下頁主訴）"),
        ],
        "flow": (
            ["輸入症狀·病史", "輸入血壓", "輸入尿液試紙", "量 SpO₂(探頭)",
             "miniPIERS 風險計算", "顯示風險/檢傷", "轉診·處置建議"],
            ["miniPIERS 風險計算"],
            {"輸入症狀·病史": "頭痛/視力、胸痛/喘、出血+腹痛、胎次、週數", "輸入血壓": "標準血壓計手動輸入",
             "輸入尿液試紙": "蛋白尿等級", "量 SpO₂(探頭)": "指夾探頭讀血氧",
             "miniPIERS 風險計算": "logistic 算 48h 危險機率", "顯示風險/檢傷": "紅綠燈式分級",
             "轉診·處置建議": "留院／治療／緊急轉診"}
        ),
        "submodules": [
            ("miniPIERS 風險模型 ★唯一模型", "多變數 Logistic 回歸（逐步後退挑變數）", "5 國 2,081 位妊娠高血壓孕婦，前瞻收案、bootstrap 內部驗證", "症狀+血壓+尿蛋白+SpO₂ → 48h 危險機率"),
            ("血氧演算（探頭）", "訊號處理（紅/紅外比值，非學習模型）", "廠商演算法", "光訊號 → SpO₂"),
        ],
        "sub_note": "本篇沒有訓練任何新模型；貢獻是把既有模型「搬到手機＋血氧計上、測好不好用」。",
        "sensors": [
            ("Phone Oximeter 指夾探頭", "血氧＋脈搏", "指尖夾在光源與感測器之間，紅／紅外光穿透，脈動訊號算出 SpO₂"),
            ("血壓計 ／ 尿液試紙", "血壓 ／ 尿蛋白", "傳統量測後手動輸入"),
            ("護理師（人為感測）", "頭痛/視力、胸痛/喘、出血+腹痛、胎次、週數", "以勾選清單輸入"),
        ],
        "results": [
            "好用性：重新設計後可用性問卷分數變好；每次完整評估中位數 4 分 55 秒",
            "內建模型 miniPIERS 判別力 AUC 0.768",
            "加入 SpO₂ 後敏感度由 ~32.8% 提升到 ~49.6%（特異度僅小降）→ 這就是要接血氧計的理由",
        ],
        "limits": [
            "只是「好用／可行」研究，沒證明能改善孕婦結局或檢傷正確率",
            "樣本小、單一國家；血氧探頭接頭易鬆、手機電力撐不了一整天",
            "血壓與試紙要人工輸入，資料品質看操作者",
            "模型判別力中等(AUC~0.77)、敏感度不高；App 不開源",
        ],
        "hl": ("每人耗時", "5 分鐘", "含所有量測與計算"),
    },
    {
        "num": "3", "kicker": "論文 3 · COVID 居家遠端監測",
        "title": "e-CoVig：COVID-19 症狀遠端監測的 mHealth 系統",
        "citation": "Raposo A, Marques L, Correia R, et al. e-CoVig: a novel mHealth system for remote monitoring of symptoms in COVID-19. Sensors. 2021;21(10):3397.",
        "cit": "引用數 未確認（估計數十）", "if": "IF ≈ 3.8（Sensors，2021）", "year": "2021",
        "one": "免費 App ＋一個自製便宜小裝置，讓病人在家自己量體溫、血氧、心率、錄咳嗽，全部自動上傳給醫院看。",
        "lay": "COVID 期間，居家隔離的病人主要靠護理師打電話追蹤，慢又給不了醫師硬數據。里斯本這團隊做了 e-CoVig：一個免費手機 App，加一個選配的便宜插件，讓病人自己量發燒、血氧、心率、錄咳嗽和呼吸、填症狀清單，全自動送到醫院的網頁儀表板。醫師就能一次盯很多病人、快速找出正在惡化的人，而不是靠一通電話。本篇是「我們把系統做出來並讓它能動」的工程報告，不是臨床試驗：它描述硬體、App 與雲端，展示訊號能被擷取，但沒有訓練診斷 AI、也沒有對 COVID 結果報準確率。",
        "problem": "COVID 高峰時，大量輕中症病人在家隔離，醫護主要靠反覆打電話追蹤——費工、只有主觀口述（沒有量到的生命徵象）、還會漏掉『無聲惡化』（尤其血氧下降）。目標使用者是居家／社區照護的 COVID 病人與追蹤他們的醫護。要解決的是：可遠端、可規模化、有客觀數據的監測與檢傷。",
        "dataset": [
            "這是「把系統做出來」的工程／概念驗證論文，沒有大型標註資料集、沒有訓練/測試切分",
            "地點：葡萄牙里斯本（IST／IT），有肺科醫師臨床參與",
            "驗證方式：技術可行性展示（自製裝置與手機相機都能取得可用訊號、OCR 能讀螢幕）",
            "沒有病人數(n)、沒有 COVID 陽/陰標籤、非公開資料集",
        ],
        "device": {
            "type": "一般手機＋Flutter App（Android，已上架 Google Play）；另有選配低成本外掛",
            "cost": "外掛：ESP32＋MAX30101（血氧/心率）＋MLX90614（紅外體溫），材料成本數十美元 → < NT$5000",
            "any_phone": ("任何現代手機", "ok"), "app": ("要（Android/Flutter）", "warn"),
            "oss": ("部分開源", "warn"), "cost_kind": "ok",
            "note": "純軟體功能（相機 PPG、麥克風、OCR）免外掛；相機 PPG 模組作者已開源，完整系統未確認開源。這篇的「融合」是靠醫師看儀表板，不是自動模型。",
        },
        "sensing": [
            ("體溫", "MLX90614 紅外線非接觸測額溫/耳溫；或用相機 OCR 讀家用體溫計螢幕"),
            ("血氧 SpO₂＋心率", "MAX30101 指尖紅/紅外光感測；或手指按後鏡頭＋閃光取得 PPG（心率）"),
            ("咳嗽·呼吸音", "手機麥克風錄音"),
            ("症狀", "App 內自填問卷"),
        ],
        "flow": (
            ["病人自填症狀", "量體溫(紅外線)", "量 SpO₂/心率", "錄咳嗽·呼吸音",
             "OCR 讀裝置螢幕", "加密上傳雲端", "醫師儀表板檢視", "檢傷/惡化標記"],
            ["OCR 讀裝置螢幕"],
            {"病人自填症狀": "填 COVID 症狀問卷", "量體溫(紅外線)": "MLX90614 或相機讀體溫計",
             "量 SpO₂/心率": "MAX30101 或相機 PPG", "錄咳嗽·呼吸音": "麥克風錄音",
             "OCR 讀裝置螢幕": "拍血氧計/體溫計螢幕自動讀數", "加密上傳雲端": "打包症狀+數據+音訊",
             "醫師儀表板檢視": "一次看多位病人趨勢", "檢傷/惡化標記": "醫師人工判讀、優先追蹤"}
        ),
        "submodules": [
            ("OCR 螢幕讀值 ★唯一學習元件", "現成 OCR 文字辨識（未自訓）", "預訓練辨識模型", "血氧計/體溫計螢幕照片 → 數字"),
            ("相機 PPG 訊號處理", "傳統訊號處理（非神經網路），已開源", "無需訓練", "指尖影片 → 脈搏波、心率"),
            ("裝置 SpO₂/HR", "MAX30101+MAX32664 韌體（廠商演算法）", "非作者訓練", "紅/紅外光 → 血氧/心率"),
            ("咳嗽/呼吸音", "只錄音上傳，未做分類器", "—", "音訊給人或後續分析"),
        ],
        "sub_note": "全系統沒有作者自訓的診斷 AI；唯一「學習」來的就是現成 OCR。",
        "sensors": [
            ("MAX30101 光學血氧感測", "血氧＋心率", "紅/紅外 LED 照指尖，測脈動血液吸光比例（MAX32664 做運算）"),
            ("手機後鏡頭＋閃光", "心率(PPG)、讀螢幕", "指尖蓋鏡頭拍血流亮暗變化；也拍螢幕給 OCR"),
            ("MLX90614 紅外線體溫", "體溫", "非接觸感測皮膚/耳朵放出的紅外線熱"),
            ("手機麥克風", "咳嗽·呼吸音", "聲學感測"),
            ("ESP32 微控制器", "（無線大腦，非感測器）", "讀各感測晶片，Wi-Fi/藍牙串流上傳"),
        ],
        "results": [
            "做出可運作的端到端系統：App ＋雲端儀表板 ＋低成本 ESP32 裝置",
            "手機與自製裝置都能取得體溫、血氧、心率、PPG；麥克風能錄咳嗽",
            "OCR 能讀商用血氧計/體溫計螢幕 → 病人可沿用手邊既有小裝置",
            "無 AUC／準確率數字，因為系統本身不做自動診斷",
        ],
        "limits": [
            "概念驗證原型，未做臨床驗證，真實檢傷效能未知",
            "無標註資料、無訓練診斷模型；咳嗽音只錄不判；症狀+數字靠醫師人工融合",
            "手機相機血氧未達醫療級（可靠 SpO₂ 要靠外掛或讀真血氧計）",
            "只在 Android 驗證；完整程式碼未全開源（僅相機 PPG 模組）",
        ],
        "hl": ("外掛材料", "數十美元", "ESP32＋感測晶片"),
    },
    {
        "num": "4", "kicker": "論文 4 · 急診檢傷的深度學習",
        "title": "用深度學習從急診檢傷的「少量資訊」揪出重症病人",
        "citation": "Joseph JW, Leventhal EL, Grossestreuer AV, et al. Deep-learning approaches to identify critically ill patients at emergency department triage using limited information. J Am Coll Emerg Physicians Open. 2020;1(5):773-781.",
        "cit": "引用數 約 30（Semantic Scholar）", "if": "IF ≈ 1.7–2.3（JACEP Open）", "year": "2020",
        "one": "不加任何硬體：把護理師打的「主訴文字」和幾個生命徵象一起丟給神經網路，就能比現行檢傷工具準很多地預測重症。",
        "lay": "病人一到急診，檢傷護理師快速記幾個生命徵象（如心率、血壓），並打一句主訴（例如「胸痛、喘」）。這研究問：電腦能不能只讀這一點點資訊，就標出可能變重症（24 小時內死亡或進加護病房）的人？研究者用約 44.6 萬筆過去就診訓練一個神經網路，發現把「打的主訴文字」和「生命徵象數字」一起用，比護理師現在用的標準檢傷工具準很多。關鍵概念是「融合」：教一個模型同時看懂文字的意義與數字。全程不需任何新裝置或感測器，準確度的提升完全來自更聰明的軟體。",
        "problem": "急診必須在幾秒到幾分鐘內、用非常少的資訊，判斷哪個到院病人即將變重症。標準工具——檢查生命徵象是否異常、或給 ESI 分級——會漏掉許多高危病人、也很主觀。低估延誤救命、高估浪費資源。本篇對象是美國一家繁忙學術急診的所有成人病人。",
        "dataset": [
            "資料：美國東北一家學術急診的私有登錄檔（非公開基準）",
            "規模：445,925 次成人就診；其中 60,901 次（13.7%）為重症",
            "時間：2012–2020；回溯性、去識別化的例行檢傷資料",
            "預測標籤：到院 24 小時內「死亡或進加護病房(ICU)」＝重症",
            "去識別子集有放到程式庫；含主訴文字的版本待機構核准",
        ],
        "device": {
            "type": "無任何硬體。純軟體／機器學習，跑在醫院既有電子病歷／檢傷系統裡",
            "cost": "無硬體成本（不需買任何東西）",
            "any_phone": ("不涉及手機", "info"), "app": ("病人端不需 App", "ok"),
            "oss": ("開源（MIT）", "ok"), "cost_kind": "ok",
            "note": "亮點是「演算法」：把主訴自由文字與既有生命徵象數字融合。程式碼公開於 github.com/jwjoseph/NN_triage_predict。",
        },
        "sensing": [
            ("生命徵象（結構化）", "心率、呼吸、血壓、體溫、血氧，加年齡/性別"),
            ("血氧／心率", "來自標準指夾血氧計"),
            ("血壓", "手臂壓脈帶"),
            ("體溫", "電子體溫計"),
            ("主訴（文字）", "護理師鍵入的一句自由文字，交給模型理解語意"),
        ],
        "flow": (
            ["病人到急診檢傷", "記生命徵象+主訴", "主訴轉詞向量", "數字正規化",
             "神經網路融合", "輸出重症機率", "門檻→高風險警示"],
            ["主訴轉詞向量", "神經網路融合", "輸出重症機率"],
            {"病人到急診檢傷": "護理師做初步評估", "記生命徵象+主訴": "量數字＋打一句主訴文字",
             "主訴轉詞向量": "每個詞轉成一串數字(embedding)", "數字正規化": "生命徵象、年齡、性別縮到同尺度",
             "神經網路融合": "共同層把文字向量＋數字一起看", "輸出重症機率": "0–1 的 24h 死亡/ICU 機率",
             "門檻→高風險警示": "超過切點→亮紅燈/調整分級"}
        ),
        "submodules": [
            ("詞向量編碼器", "學習得到的 word embeddings", "本院 ~44.6 萬筆主訴文字", "主訴斷詞 → 數值向量（意義相近的詞靠得近）"),
            ("融合神經網路 ★主模型", "前饋神經網路（sigmoid 輸出）", "445,925 次就診、24h 死亡/ICU 標籤監督學習", "詞向量＋正規化數字 → 重症機率"),
            ("純數字神經網路（對照）", "2 層全連接", "同資料，只用數字", "AUC 0.811"),
            ("梯度提升樹（對照）", "boosting 決策樹", "同數字特徵", "AUC 0.820"),
            ("Logistic 回歸（對照）", "線性基準", "同數字特徵", "AUC 0.803"),
        ],
        "sub_note": "關鍵發現：把主訴文字加進去，AUC 由最好的純數字 0.820 升到 0.851，遠勝傳統規則。",
        "sensors": [
            ("指夾血氧計 ／ 壓脈帶 ／ 體溫計", "血氧·心率 ／ 血壓 ／ 體溫", "都是急診既有標準器材，護理師量測後輸入"),
            ("護理師鍵入的主訴", "病人主觀不適（文字）", "自由文字，交給模型理解語意——這是本篇的主角"),
        ],
        "results": [
            "最佳模型＝主訴文字＋生命徵象的神經網路：AUC 0.851",
            "只用數字：神經網路 0.811、梯度提升 0.820、Logistic 0.803",
            "現行工具遠遜：生命徵象異常規則 0.521（接近瞎猜）、ESI 分級 0.672",
            "白話：把那句主訴加進去，就比最好的純數字模型再高 3+ 分，更電輾傳統規則",
        ],
        "limits": [
            "單中心、回溯資料，是否能搬到別家醫院未驗證",
            "標籤（24h 死亡/ICU）是重症替身，受住院習慣影響",
            "主訴文字因人而異、有縮寫錯字，換地方可能變差",
            "只證明『預測更準』，沒證明改善病人結局；神經網路是黑盒、可解釋性低",
        ],
        "hl": ("最佳 AUC", "0.851", "對比 ESI 只有 0.672"),
    },
    {
        "num": "5", "kicker": "論文 5 · 手機相機測血氧（原理）",
        "title": "智慧手機相機血氧偵測：誘導低血氧研究",
        "citation": "Hoffman JS, Viswanath VK, Tian C, et al. Smartphone camera oximetry in an induced hypoxemia study. npj Digit Med. 2022;5(1):146.（華盛頓大學 UbiComp Lab）",
        "cit": "引用數 約 25（估計）", "if": "IF ≈ 14.8（npj Digital Medicine，2022；極高）", "year": "2022",
        "one": "把手指按在「沒改裝的普通手機」後鏡頭上、開閃光，軟體讀血液細微的顏色閃動，就能估血氧——正是你說的『手指按相機測血氧』。",
        "lay": "血液需要足夠氧氣；太低（叫低血氧）是 COVID、氣喘、慢性肺病等危險的警訊。醫師平常用夾手指的血氧計量血氧（SpO₂）。這研究問：一支普通、沒改裝的手機能不能做同樣的事？你把手指按在手機後鏡頭上、開閃光，軟體讀血液的細微顏色閃動來估氧氣。為了公平測試，六位志願者在診所安全地吸入低氧氣體，讓真實血氧一路降到約 70%，再讓一個神經網路學著預測。手機方法平均誤差約 5 個百分點、能正確標出約 8 成的危險低值——有潛力，但仍不如真正的醫療血氧計準。",
        "problem": "低血氧（SpO₂ 偏低）是 COVID、氣喘、慢性阻塞性肺病、肺炎等惡化的早期警訊。標準的夾式血氧計準，但很多人沒有，尤其資源不足地區。如果普通手機靠一次軟體更新就能量血氧，幾十億人就多了一個便宜、隨手可得的篩檢工具。本篇對象是健康成人志願者（用來建立與驗證方法），屬概念驗證，不是對病人的部署試驗。",
        "dataset": [
            "6 位健康成人（編號 10001–10006），在認證實驗室（Clinimark）做「誘導低血氧」",
            "受試者吸入受控低氧氣體，血氧安全地一階一階降到約 70%（個別讀值低至 ~61%）",
            "比過去手機研究（只到 85–100%）涵蓋更廣的危險範圍",
            "收集 >10,000 對血氧讀值；真值來自 FDA 核准的參考血氧計；相機 30Hz 記錄",
            "評估：留一受試者法（用其他 5 人訓練、測從沒看過的第 6 人）",
            "資料集＋範例程式公開（MIT）：github.com/ubicomplab/oximetry-phone-cam-data",
        ],
        "device": {
            "type": "未改裝的市售手機（Google Nexus 6P）：手指蓋後鏡頭、開閃光即可",
            "cost": "幾乎零成本（用手邊既有手機）→ 遠 < NT$5000",
            "any_phone": ("原理上任何手機", "warn"), "app": ("要擷取用 App", "warn"),
            "oss": ("資料＋程式開源(MIT)", "ok"), "cost_kind": "ok",
            "note": "只在單一機型（Nexus 6P）驗證，跨機型未證實。App 固定了相機色彩增益（紅1x/綠3x/藍18x），讓穿過手指的微弱藍綠光可用。未推出消費者產品。",
        },
        "sensing": [
            ("血氧 SpO₂", "手指蓋後鏡頭、閃光從內照亮組織；相機逐格記錄血液脈動造成的細微顏色(RGB)變化＝PPG 訊號"),
            ("原理 ratio-of-ratios", "含氧與缺氧血紅素對紅光 vs 藍/綠光吸收不同；比較各色『脈動(AC)/穩定(DC)』比值 → 反推含氧量"),
            ("心率", "PPG 的脈動頻率本身就含心率"),
        ],
        "flow": (
            ["手指按相機+閃光", "錄 RGB 影片(30Hz)", "抽取 R/G/B 脈搏", "濾波·正規化 PPG",
             "算 ratio-of-ratios", "CNN 回歸血氧", "輸出 SpO₂ 估計", "90% 門檻→低血氧警示"],
            ["CNN 回歸血氧"],
            {"手指按相機+閃光": "閃光從內照亮指尖組織", "錄 RGB 影片(30Hz)": "固定色彩增益抓微弱光",
             "抽取 R/G/B 脈搏": "每格平均成紅綠藍三條脈動波", "濾波·正規化 PPG": "去漂移雜訊、分 AC/DC",
             "算 ratio-of-ratios": "各色 AC/DC 比值＝含氧指標", "CNN 回歸血氧": "卷積網路模仿血氧物理",
             "輸出 SpO₂ 估計": "預測未看過者的血氧", "90% 門檻→低血氧警示": "低於 90% 判為低血氧"}
        ),
        "submodules": [
            ("CNN 血氧估計 ★唯一模型", "卷積神經網路（刻意模仿 ratio-of-ratios 物理）", "誘導低血氧資料的『顏色訊號→血氧』配對；真值來自 FDA 核准血氧計；留一受試者驗證", "R/G/B 相機 PPG → SpO₂"),
            ("ratio-of-ratios 特徵", "解析式訊號處理（非學習）", "無需訓練", "AC/DC 比值 → 含氧指標"),
        ],
        "sub_note": "CNN 設計上要（1）壓低心跳變異影響、（2）處理手機相機的雜訊。",
        "sensors": [
            ("手機後鏡頭（CMOS）", "R/G/B 反射光", "手指蓋鏡頭、閃光照亮，逐格量返回的紅綠藍光；每次心跳血量增加→返回光忽暗忽亮＝脈搏"),
            ("LED 閃光燈", "光源", "提供穿透手指、可被血液吸收的光，是反射式量測的必要光源"),
        ],
        "results": [
            "留一受試者下，深度學習估血氧平均絕對誤差(MAE) 5.00%（σ 1.90），涵蓋 70–100%",
            "偵測低血氧(SpO₂<90%)：敏感度約 81%、特異度約 79%",
            "白話：平均離真值約 5 分，10 個危險讀值抓到約 8 個",
            "對照：FDA 建議血氧計誤差 <3.5% → 有潛力但還沒到醫療級",
        ],
        "limits": [
            "樣本極小（6 位健康人），不一定適用真實病人／長者／有病者",
            "只用單一機型（Nexus 6P），跨手機未驗證",
            "MAE 5% 超過 FDA <3.5% 建議 → 屬篩檢/概念驗證，非診斷級",
            "膚色多樣性有限（已知會影響血氧量測）；且在無動作的實驗室條件下測",
        ],
        "hl": ("平均誤差", "MAE 5.0%", "低血氧偵測 81% 敏感度"),
    },
]


def _badges_row(slide, top, dev):
    items = [
        ("任何手機都能用？", dev["any_phone"][0], dev["any_phone"][1]),
        ("需要 App？", dev["app"][0], dev["app"][1]),
        ("開源？", dev["oss"][0], dev["oss"][1]),
        ("成本 vs NT$5000", "低成本" if dev["cost_kind"] == "ok" else ("超過" if dev["cost_kind"] == "warn" else "不適用"), dev["cost_kind"]),
    ]
    x = Inches(0.78); w = Inches(2.82); gap = Inches(0.14)
    for lab, val, kind in items:
        badge(slide, x, top, lab, val, kind=kind, w=w, h=Inches(0.78))
        x += w + gap


def render_paper(prs, p):
    accent = ACCENT
    # ---------- Slide A: header
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    rect(s, 0, 0, SW, Inches(1.95), fill=PRIMARY)
    rect(s, 0, 0, Inches(0.22), Inches(1.95), fill=ACCENT)
    # big number faint
    tfn = textbox(s, Inches(11.4), Inches(0.15), Inches(1.8), Inches(1.7))
    para(tfn, p["num"], 60, RGBColor(0x2A, 0x6A, 0x83), bold=True, align=PP_ALIGN.RIGHT, first=True)
    tf = textbox(s, Inches(0.78), Inches(0.34), Inches(10.6), Inches(1.4))
    para(tf, p["kicker"], 12, RGBColor(0xBF, 0xDD, 0xE7), bold=True, space_after=4, first=True)
    para(tf, p["title"], 21, WHITE, bold=True, line_spacing=1.02)
    # chips
    x = Inches(0.78); y = Inches(2.15)
    for t, c in [(p["cit"], ACCENT), (p["if"], PRIMARY), (p["year"], MUTED)]:
        _, w = chip(s, x, y, t, fill=PANEL2, fg=c, h=Inches(0.36)); x += w + Inches(0.16)
    # citation
    tf = textbox(s, Inches(0.78), Inches(2.68), Inches(11.75), Inches(0.85))
    para(tf, "出處：" + p["citation"], 10, MUTED, italic=True, first=True, line_spacing=1.12)
    # one-line callout
    callout(s, Inches(0.78), Inches(3.62), Inches(11.75), Inches(0.92), "一句話看懂", p["one"], accent=MODEL, fill=MODELBG)
    # lay summary panel
    _, lx, ly, lw = panel_titled(s, Inches(0.78), Inches(4.75), Inches(11.75), Inches(2.05), "這篇在做什麼？（白話）")
    tf = textbox(s, lx, ly, lw, Inches(1.5))
    para(tf, p["lay"], 12, BODY, first=True, line_spacing=1.28)
    footer(s)
    notes(s, "【給講者的白話稿】\n一句話：" + p["one"] + "\n\n為什麼重要（臨床問題）：" + p["problem"] +
          "\n\n白話總結：" + p["lay"])

    # ---------- Slide B: problem + dataset
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, p["kicker"], "① 臨床問題　＋　② 在什麼資料上訓練", num=None)
    _, ax, ay, aw = panel_titled(s, Inches(0.78), Inches(1.6), Inches(5.6), Inches(5.0), "臨床問題（為什麼重要）", accent=MODEL, fill=MODELBG)
    tf = textbox(s, ax, ay, aw, Inches(4.0))
    para(tf, p["problem"], 12.5, BODY, first=True, line_spacing=1.32)
    _, bx, by, bw = panel_titled(s, Inches(6.6), Inches(1.6), Inches(5.95), Inches(5.0), "資料集 Dataset")
    _bullets(s, bx, by, bw, p["dataset"], size=12, gap=9)
    footer(s)

    # ---------- Slide C: device + cost + sensing
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, p["kicker"], "③ 設備 · 推測金額 · 怎麼取得徵象", num=None)
    _badges_row(s, Inches(1.5), p["device"])
    # device type + cost line
    tf = textbox(s, Inches(0.78), Inches(2.45), Inches(11.75), Inches(0.9))
    para(tf, [("設備：", True, PRIMARY), (p["device"]["type"], False, BODY)], 12, first=True, line_spacing=1.15)
    para(tf, [("金額：", True, PRIMARY), (p["device"]["cost"], False, BODY)], 12, line_spacing=1.15, space_before=3)
    callout(s, Inches(0.78), Inches(3.5), Inches(11.75), Inches(0.92), "", p["device"]["note"], accent=AMBER, fill=RGBColor(0xFC,0xF4,0xE4))
    # sensing
    _, sx, sy, sw = panel_titled(s, Inches(0.78), Inches(4.62), Inches(11.75), Inches(2.2), "量哪些徵象、怎麼取得")
    _sensing_rows(s, sx, sy, sw, p["sensing"])
    footer(s)

    # ---------- Slide D: flow diagram
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, p["kicker"], "④ 完整流程圖（橘框＝需訓練的模型）", num=None)
    labels, models, details = p["flow"]
    flow_snake(s, Inches(0.78), Inches(1.85), Inches(11.75), labels, models, details,
               box_h=Inches(1.05), max_cols=(4 if len(labels) <= 4 else 4 if len(labels) == 7 else 4))
    # one-line under flow
    callout(s, Inches(0.78), Inches(6.15), Inches(11.75), Inches(0.62), "",
            "藍框＝一般步驟（量測/輸入/顯示）；橘框＝從資料學來的模型。順著箭頭看，就是這篇的完整運作。", accent=PRIMARY, fill=PANEL)
    footer(s)
    steps_note = "【流程逐步講解】\n" + "\n".join(
        f"{i+1}. {lab}：{details.get(lab, '')}" for i, lab in enumerate(labels))
    notes(s, steps_note)

    # ---------- Slide E: submodules + sensors
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, p["kicker"], "④ 各子模組的訓練　＋　各感測器介紹", num=None)
    _, mx, my, mw = panel_titled(s, Inches(0.78), Inches(1.6), Inches(6.6), Inches(5.0), "子模組（怎麼訓練的）")
    note_h = Inches(0.62) if p.get("sub_note") else Inches(0)
    avail = Inches(6.55) - my - note_h        # panel bottom ~6.6
    end_y = _submodule_cards(s, mx, my, mw, p["submodules"], avail)
    if p.get("sub_note"):
        tfn = textbox(s, mx, end_y + Inches(0.04), mw, note_h)
        para(tfn, "※ " + p["sub_note"], 10.5, MODEL, bold=True, first=True, line_spacing=1.1)
    _, cx, cy, cw = panel_titled(s, Inches(7.55), Inches(1.6), Inches(5.0), Inches(5.0), "感測器逐個看", accent=ACCENT, fill=RGBColor(0xED,0xF6,0xF8))
    _sensor_cards(s, cx, cy, cw, p["sensors"])
    footer(s)

    # ---------- Slide F: results + limits
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, p["kicker"], "結果重點　＋　限制與注意", num=None)
    # highlight number box
    hk, hv, hd = p["hl"]
    hb = rect(s, Inches(0.78), Inches(1.6), Inches(3.2), Inches(2.0), fill=PRIMARY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    tf = textbox(s, Inches(0.95), Inches(1.75), Inches(2.9), Inches(1.75), anchor=MSO_ANCHOR.MIDDLE)
    para(tf, hk, 12, RGBColor(0xBF,0xDD,0xE7), bold=True, align=PP_ALIGN.CENTER, first=True, space_after=4)
    para(tf, hv, 30, WHITE, bold=True, align=PP_ALIGN.CENTER, space_after=4)
    para(tf, hd, 10.5, RGBColor(0xCF,0xE2,0xEA), align=PP_ALIGN.CENTER, line_spacing=1.05)
    _, rx, ry, rw = panel_titled(s, Inches(4.2), Inches(1.6), Inches(8.35), Inches(2.0), "結果重點", accent=GREEN, fill=RGBColor(0xEC,0xF6,0xF0))
    _bullets(s, rx, ry, rw, p["results"], size=11.5, gap=5)
    _, lx, ly, lw = panel_titled(s, Inches(0.78), Inches(3.85), Inches(11.75), Inches(2.85), "限制與注意（不能過度樂觀的地方）", accent=RED, fill=RGBColor(0xFA,0xEE,0xF0))
    _bullets(s, lx, ly, lw, p["limits"], size=12, gap=8)
    footer(s)
    notes(s, "【結果重點】\n" + "\n".join("· " + r for r in p["results"]) +
          "\n\n【限制】\n" + "\n".join("· " + r for r in p["limits"]))


def render_compare(prs):
    # ---- Table A: device / cost / vitals
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "綜合比較 ①", "五篇一次看懂：設備 · 成本 · 量到的徵象", num=None)
    headers = ["#　論文", "設備型態", "推測金額", "< NT$5000?", "量到的徵象"]
    col_w = [Inches(2.35), Inches(2.5), Inches(2.5), Inches(1.6), Inches(2.8)]
    rows = [
        ["1　Smart Triage", "平板＋夾式血氧計", "約 NT$1.3–1.7 萬", "否（超過）", "血氧·心率·體溫·呼吸·上臂圍"],
        ["2　PIERS on Move", "手機＋血氧探頭", "約 NT$1–2 千", "是", "血氧·脈搏·血壓·尿蛋白"],
        ["3　e-CoVig", "手機＋DIY 外掛", "材料 數十美元", "是", "體溫·血氧·心率·咳嗽音"],
        ["4　Joseph 2020", "無（純軟體）", "無硬體", "是", "急診既有生命徵象"],
        ["5　Hoffman 2022", "純手機相機", "≈ 0（用既有機）", "是", "血氧 SpO₂"],
    ]
    simple_table(s, Inches(0.78), Inches(1.75), col_w, headers, rows, row_h=Inches(0.82), fs=11)
    callout(s, Inches(0.78), Inches(6.3), Inches(11.75), Inches(0.55), "",
            "真正「便宜（<NT$5000）」的是純手機、DIY 外掛、純軟體；醫療級夾式血氧計整套會超過。", accent=PRIMARY, fill=PANEL)
    footer(s)

    # ---- Table B: chief complaint / model / data / output / oss
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "綜合比較 ②", "五篇一次看懂：主訴 · 模型 · 資料 · 輸出 · 開源", num=None)
    headers = ["#　論文", "用主訴?", "核心模型", "訓練資料", "檢傷輸出", "開源?"]
    col_w = [Inches(2.1), Inches(1.75), Inches(2.7), Inches(2.35), Inches(2.05), Inches(0.85)]
    rows = [
        ["1　Smart Triage", "是·勾選", "Logistic 回歸（9 變數）", "烏干達 1,612 童", "紅/黃/綠三級", "否"],
        ["2　PIERS", "是·勾選", "miniPIERS Logistic", "5 國 2,081 孕婦", "48h 危險機率", "否"],
        ["3　e-CoVig", "是·人工融合", "無自訓模型（僅 OCR）", "無（概念驗證）", "儀表板·人工判", "部分"],
        ["4　Joseph", "是·文字/深度學習", "神經網路（文字＋數字）", "44.6 萬急診就診", "24h 重症機率", "是·MIT"],
        ["5　Hoffman", "否", "CNN（相機 PPG）", "6 人誘導低血氧", "血氧＋90% 門檻", "是·MIT"],
    ]
    simple_table(s, Inches(0.78), Inches(1.75), col_w, headers, rows, row_h=Inches(0.82), fs=10.5)
    callout(s, Inches(0.78), Inches(6.3), Inches(11.75), Inches(0.55), "",
            "想自己動手：第 4 篇 Joseph（開源程式）＋第 5 篇 Hoffman（開源資料）最好上手。", accent=MODEL, fill=MODELBG)
    footer(s)


def render_takeaways(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "重點總結", "看完這 5 篇，你該記住的 6 件事", num=None)
    pts = [
        ("① 已有多種可行做法", "用便宜設備＋主訴做檢傷，橫跨兒科、產科、COVID、急診——不是紙上談兵。"),
        ("② 兩條融合路線", "A：把數字＋主訴丟給模型自動算（1、2、4、5）；B：資料上傳、讓醫師在儀表板判（3）。"),
        ("③ 主訴很有價值", "Joseph 用數字證明：加入主訴文字，AUC 由 0.82 升到 0.85，遠勝傳統 ESI 0.67。"),
        ("④ 手機測血氧的原理", "Hoffman 說清楚：手指按相機＋閃光→血液顏色閃動(PPG)→ratio-of-ratios→CNN 估血氧。"),
        ("⑤ 「便宜」有分寸", "純手機/麥克風/ESP32/純軟體 真的 <NT$5000；醫療級夾式血氧計整套會超過。"),
        ("⑥ 多為概念驗證", "多是單中心/小樣本，離「臨床證明能救命」還有距離；開源程度不一（4、5 開源）。"),
    ]
    for i, (t, d) in enumerate(pts):
        col = i // 3
        row = i % 3
        x = Inches(0.78) + col * Inches(6.0)
        y = Inches(1.7) + row * Inches(1.7)
        sp = rect(s, x, y, Inches(5.75), Inches(1.5), fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
        rect(s, x, y, Inches(0.1), Inches(1.5), fill=(MODEL if i in (2, 3) else ACCENT))
        tf = textbox(s, x + Inches(0.28), y + Inches(0.16), Inches(5.3), Inches(1.2))
        para(tf, t, 13, PRIMARY, bold=True, space_after=4, first=True)
        para(tf, d, 11, BODY, line_spacing=1.16)
    footer(s)


def render_sources(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "資料可信度說明", "關於引用數、impact factor 與一個更正", num=None)
    _, ax, ay, aw = panel_titled(s, Inches(0.78), Inches(1.65), Inches(11.75), Inches(2.2), "引用數與 impact factor 怎麼看", accent=AMBER, fill=RGBColor(0xFC,0xF4,0xE4))
    _bullets(s, ax, ay, aw, [
        "本簡報製作環境的網路代理擋住了 Google Scholar / Semantic Scholar，因此「引用數」多為估計值，並標註來源（如 Crossref、Semantic Scholar），請當作參考下限。",
        "「impact factor」取自 JCR 或第三方彙整（如 Scopus CiteScore），並標註年份；部分期刊在論文發表當年尚無成熟 IF（如 JACEP Open、JMIR mHealth 早年）。",
        "各篇論文全文多數也被代理擋下，內容主要由多來源搜尋摘要交叉比對而成；關鍵數字（樣本數、AUC、模型公式）在多處一致，可信度較高。",
    ], size=11.5, gap=8)
    _, bx, by, bw = panel_titled(s, Inches(0.78), Inches(4.05), Inches(11.75), Inches(2.3), "一個重要更正", accent=RED, fill=RGBColor(0xFA,0xEE,0xF0))
    _bullets(s, bx, by, bw, [
        "查證時發現：Smart Triage（第 1 篇）常被口耳相傳成「XGBoost」，但實際發表的模型是「多變數 Logistic 回歸 ＋ bootstrap 逐步選變數」，共 9 個預測因子。本簡報以論文原文為準。",
        "這也提醒：二手資訊常有誤差，重要結論最好回到原始論文核對。",
    ], size=12, gap=8)
    footer(s)


def render_references(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "參考文獻", "5 篇主論文 ＋ 內含模型來源", num=None)
    refs = [
        "1. Mawji A, Li E, Dunsmuir D, et al. Smart triage: development of a rapid pediatric triage algorithm for use in low-and-middle income countries. Front Pediatr. 2022;10:976870.",
        "　  外部驗證：Kigo J, et al. External validation of a paediatric Smart Triage model for use in resource limited facilities. PLOS Digit Health. 2024;3(6):e0000293.",
        "2. Lim J, Cloete G, Dunsmuir DT, et al. Usability and feasibility of PIERS on the Move: an mHealth app for pre-eclampsia triage. JMIR Mhealth Uhealth. 2015;3(2):e37.",
        "　  模型來源：Payne BA, Hutcheon JA, Ansermino JM, et al. miniPIERS: a risk prediction model for pre-eclampsia. PLoS Med. 2014;11(1):e1001589.",
        "3. Raposo A, Marques L, Correia R, et al. e-CoVig: a novel mHealth system for remote monitoring of symptoms in COVID-19. Sensors. 2021;21(10):3397.",
        "4. Joseph JW, Leventhal EL, Grossestreuer AV, et al. Deep-learning approaches to identify critically ill patients at emergency department triage using limited information. J Am Coll Emerg Physicians Open. 2020;1(5):773-781.",
        "5. Hoffman JS, Viswanath VK, Tian C, et al. Smartphone camera oximetry in an induced hypoxemia study. npj Digit Med. 2022;5(1):146.",
    ]
    tf = textbox(s, Inches(0.78), Inches(1.7), Inches(11.75), Inches(5.0))
    first = True
    for r in refs:
        para(tf, r, 11.5, BODY, first=first, space_after=9, line_spacing=1.2)
        first = False
    # open code/data chips
    y = Inches(6.15)
    tf2 = textbox(s, Inches(0.78), y, Inches(11.75), Inches(0.6))
    para(tf2, [("開源資源：", True, PRIMARY),
               ("Joseph 程式 github.com/jwjoseph/NN_triage_predict　·　Hoffman 資料 github.com/ubicomplab/oximetry-phone-cam-data　·　e-CoVig 相機PPG github.com/Afonsocraposo/ppg", False, MUTED)],
         10, first=True, line_spacing=1.15)
    footer(s)


def render_glossary2(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=BG)
    title_bar(s, "名詞附錄", "AI 與醫療名詞小辭典（進階）", num=None)
    terms = [
        ("Logistic 回歸", "把幾個輸入加權後輸出「0–1 機率」的統計公式；簡單、可解釋。"),
        ("神經網路 / 深度學習", "多層、會自己從資料學規則的模型；能處理文字、影像等複雜輸入。"),
        ("CNN 卷積神經網路", "擅長從訊號/影像抓局部特徵的一種神經網路。"),
        ("詞向量 word embedding", "把每個字詞變成一串數字，意義相近的詞數字也相近，讓模型「讀懂」文字。"),
        ("AUROC / AUC", "模型排序準不準的分數：0.5＝瞎猜、1.0＝完美；0.8 已算不錯。"),
        ("敏感度 / 特異度", "抓到真病人的比例 / 正確放行沒事者的比例；兩者常需取捨。"),
        ("ratio-of-ratios", "血氧計核心算式：比較兩色光『脈動/穩定』吸光比 → 反推含氧量。"),
        ("ESI", "美國急診 5 級檢傷量表，是常見的傳統比較基準。"),
        ("MUAC 上臂圍", "量上臂一圈，快速反映兒童營養/病況的指標。"),
        ("概念驗證 / 留一驗證", "先證明「做得出來」；留一：用其他人訓練、測沒看過的那個人。"),
    ]
    col_w = Inches(5.85)
    xs = [Inches(0.78), Inches(6.95)]
    for i, (term, desc) in enumerate(terms):
        col = i // 5; row = i % 5
        x = xs[col]; y = Inches(1.7) + Inches(row * 1.02)
        sp = rect(s, x, y, col_w, Inches(0.9), fill=PANEL, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
        rect(s, x, y, Inches(0.09), Inches(0.9), fill=ACCENT)
        tf = textbox(s, x + Inches(0.26), y + Inches(0.1), col_w - Inches(0.4), Inches(0.72))
        para(tf, term, 12, PRIMARY, bold=True, space_after=2, first=True)
        para(tf, desc, 10.3, BODY, line_spacing=1.08)
    footer(s)


def render_closing(prs):
    s = _blank(prs)
    rect(s, 0, 0, SW, SH, fill=PRIMD)
    rect(s, 0, 0, Inches(0.24), SH, fill=ACCENT)
    tf = textbox(s, Inches(0.95), Inches(2.2), Inches(11), Inches(2.6))
    para(tf, "一句話帶走", 14, ACCENT, bold=True, space_after=10, first=True)
    para(tf, "只要「便宜設備量到徵象」＋「聽懂病人主訴」，", 24, WHITE, bold=True, line_spacing=1.15)
    para(tf, "再交給對的模型或醫師，就能在沒有專業設備時做出不錯的初步檢傷。", 24, WHITE, bold=True, line_spacing=1.15)
    tf2 = textbox(s, Inches(0.95), Inches(5.2), Inches(11), Inches(1))
    para(tf2, "謝謝觀看 · 5 篇論文導讀完", 14, RGBColor(0xBF,0xDD,0xE7), first=True)
    return s


def _sensing_rows(slide, x, y, w, sensing):
    n = len(sensing)
    col_w = (w - Inches(0.3)) / 2
    per_col = (n + 1) // 2
    for i, (sign, how) in enumerate(sensing):
        col = i // per_col
        row = i % per_col
        cx = x + col * (col_w + Inches(0.3))
        cy = y + row * Inches(0.5)
        rect(slide, cx, cy + Inches(0.06), Inches(0.14), Inches(0.14), fill=ACCENT, shape=MSO_SHAPE.OVAL)
        tf = textbox(slide, cx + Inches(0.28), cy - Inches(0.02), col_w - Inches(0.3), Inches(0.5))
        para(tf, [(sign + "：", True, INK), (how, False, BODY)], 10.5, first=True, line_spacing=1.05)


def _submodule_cards(slide, x, y, w, subs, avail_h=Inches(4.3)):
    n = max(1, len(subs))
    gap = Inches(0.08)
    ch = int((avail_h - gap * (n - 1)) / n)
    ch = max(Inches(0.62), min(Inches(1.02), ch))
    for i, (name, algo, trained, io) in enumerate(subs):
        cy = y + i * (ch + gap)
        is_star = "★" in name
        rect(slide, x, cy, w, ch, fill=(MODELBG if is_star else WHITE), line=(MODEL if is_star else LINE), line_w=1.2,
             shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
        tf = textbox(slide, x + Inches(0.15), cy + Inches(0.07), w - Inches(0.3), ch - Inches(0.12))
        para(tf, [(name + "　", True, (MODEL if is_star else PRIMARY)), ("· " + algo, False, MUTED)], 10.5, first=True, space_after=1, line_spacing=1.0)
        para(tf, [("訓練：", True, BODY), (trained, False, BODY)], 9.3, space_after=0, line_spacing=1.02)
        para(tf, [("輸入→輸出：", True, BODY), (io, False, BODY)], 9.3, line_spacing=1.02)
    return y + n * (ch + gap)


def _sensor_cards(slide, x, y, w, sensors):
    ch = min(Inches(1.12), (Inches(4.5)) / max(1, len(sensors)))
    for i, (name, measures, principle) in enumerate(sensors):
        cy = y + i * (ch + Inches(0.08))
        rect(slide, x, cy, w, ch, fill=WHITE, line=ACCENT, line_w=1.0, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
        rect(slide, x, cy, Inches(0.08), ch, fill=ACCENT)
        tf = textbox(slide, x + Inches(0.2), cy + Inches(0.06), w - Inches(0.3), ch - Inches(0.1))
        para(tf, [(name + "　", True, PRIMARY), ("｜ " + measures, False, MUTED)], 10, first=True, space_after=1, line_spacing=1.0)
        para(tf, principle, 9.3, BODY, line_spacing=1.05)
