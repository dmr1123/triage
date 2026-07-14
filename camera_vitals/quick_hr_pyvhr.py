# -*- coding: utf-8 -*-
"""
最快版：用 pyVHR 直接吃一段影片 → 估心率(HR)。classical rPPG，不用權重、不用訓練。
先用這支證明「相機測心率在你的影片上到底行不行」。RR 請用 infer_rppg.py。

安裝：
    pip install pyVHR          # 或 pip install pyvhr
    # 相依：mediapipe、numba、torch、opencv-python（pyVHR 會一起帶）

用法：
    python quick_hr_pyvhr.py --video myclip.mp4

注意：pyVHR 各版本 API 略有差異；若 run_on_video 參數對不上，
      參考 https://github.com/phuselab/pyVHR 的 README（下方已標可能要改的行）。
"""
import argparse
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="臉部影片（正面、光線足、盡量不晃）")
    args = ap.parse_args()

    # pyVHR 2.x 的高階管線
    from pyVHR.analysis.pipeline import Pipeline

    pipe = Pipeline()
    # ↓↓↓ 【本機可能要調】不同版本參數名可能不同（roi_approach/roi_method/method/bpm_type）
    time, bpm, uncertainty = pipe.run_on_video(
        args.video,
        roi_approach="holistic",     # 整張臉當 ROI（也可 "patches"）
        roi_method="convexhull",     # 用臉部關鍵點取膚色區
        method="cpu_POS",            # POS 演算法（穩、免 GPU）；也可 "cpu_CHROM"
        bpm_type="welch",            # 用 Welch 頻譜估 BPM
        cuda=False,
        verb=True,
    )

    bpm = np.asarray(bpm, dtype=float)
    bpm = bpm[np.isfinite(bpm)]
    result = {
        "median_hr_bpm": round(float(np.median(bpm)), 1) if bpm.size else None,
        "mean_hr_bpm": round(float(np.mean(bpm)), 1) if bpm.size else None,
        "n_windows": int(bpm.size),
    }
    print(result)


if __name__ == "__main__":
    main()
