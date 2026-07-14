# -*- coding: utf-8 -*-
"""
video -> {hr, rr} 用 rPPG-Toolbox 的『pretrained TS-CAN』估心率(HR)，
外加一個『呼吸基線調變』估呼吸率(RR，近似值)。

★ 一定要在 rPPG-Toolbox 的 repo 根目錄下、且在 rppg-toolbox 環境裡執行，
  這樣 `dataset / neural_methods / evaluation` 才 import 得到。

準備：
    git clone https://github.com/ubicomplab/rPPG-Toolbox
    cd rPPG-Toolbox
    bash setup.sh conda && conda activate rppg-toolbox
    ls final_model_release/          # ← 看有哪些 .pth 權重（例如 PURE_TSCAN.pth）
    # 把本檔放到這個 repo 根目錄

用法：
    # 臉部影片：
    python infer_rppg.py --video myclip.mp4 --weights final_model_release/PURE_TSCAN.pth --roi face
    # 手指按鏡頭(指尖 PPG)：用 --roi full（不做人臉偵測）
    python infer_rppg.py --video finger.mp4 --weights final_model_release/PURE_TSCAN.pth --roi full

★★ 版本敏感、務必本機核對（否則權重載不進去或形狀對不上）：
   --img_size 要等於「訓練該權重的 config 的 RESIZE 尺寸」（標準 TSCAN 多為 72）
   --frame_depth 要等於該 config 的 MODEL.TSCAN.FRAME_DEPTH（常見 10 或 20）
   → 去 configs/ 找對應的 YAML 看這兩個值。權重檔名/路徑也用 ls 確認。
"""
import argparse
import json
import numpy as np
import cv2
import torch

# 官方模組（在 repo 根目錄執行才 import 得到）
from dataset.data_loader.BaseLoader import BaseLoader
from neural_methods.model.TS_CAN import TSCAN
from evaluation.post_process import _calculate_fft_hr


def read_frames(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(f, cv2.COLOR_BGR2RGB))
    cap.release()
    if not frames:
        raise RuntimeError("讀不到影格，檢查影片路徑/編碼。")
    return np.asarray(frames, dtype=np.float32), float(fps)


def crop_face(frames, size):
    """用 OpenCV Haar 偵測第一張臉，之後固定框裁切→resize。偵測不到就置中裁切。"""
    casc = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    g = cv2.cvtColor(frames[0].astype(np.uint8), cv2.COLOR_RGB2GRAY)
    faces = casc.detectMultiScale(g, 1.2, 5)
    out = []
    if len(faces):
        x, y, w, h = sorted(faces, key=lambda b: b[2] * b[3])[-1]
        cx, cy, s = x + w // 2, y + h // 2, int(max(w, h) * 1.2 // 2)
        for f in frames:
            H, W, _ = f.shape
            x0, y0 = max(0, cx - s), max(0, cy - s)
            x1, y1 = min(W, cx + s), min(H, cy + s)
            out.append(cv2.resize(f[y0:y1, x0:x1], (size, size)))
    else:
        for f in frames:
            H, W, _ = f.shape
            s = min(H, W); y0 = (H - s) // 2; x0 = (W - s) // 2
            out.append(cv2.resize(f[y0:y0 + s, x0:x0 + s], (size, size)))
    return np.asarray(out, dtype=np.float32)


def resize_full(frames, size):
    return np.asarray([cv2.resize(f, (size, size)) for f in frames], dtype=np.float32)


def fft_rate(sig, fs, lo, hi):
    """單一訊號 → 頻帶內主頻（次/分）。"""
    sig = np.asarray(sig, dtype=float)
    sig = sig - sig.mean()
    n = len(sig)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    power = np.abs(np.fft.rfft(sig)) ** 2
    band = (freqs >= lo) & (freqs <= hi)
    if not band.any():
        return float("nan")
    return float(freqs[band][np.argmax(power[band])] * 60.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--weights", required=True, help="final_model_release/ 底下的 .pth")
    ap.add_argument("--roi", choices=["face", "full"], default="face")
    ap.add_argument("--img_size", type=int, default=72)     # ★ 對齊訓練 config 的 RESIZE
    ap.add_argument("--frame_depth", type=int, default=20)  # ★ 對齊 MODEL.TSCAN.FRAME_DEPTH
    args = ap.parse_args()

    frames, fps = read_frames(args.video)
    roi = crop_face(frames, args.img_size) if args.roi == "face" else resize_full(frames, args.img_size)

    # 官方預處理：前 3 通道 DiffNormalized、後 3 通道 Standardized（順序要和 TS-CAN forward 一致）
    diff = BaseLoader.diff_normalize_data(roi)   # (T,H,W,3)
    std = BaseLoader.standardized_data(roi)      # (T,H,W,3)
    x = np.concatenate([diff, std], axis=-1)     # (T,H,W,6)

    T = (len(x) // args.frame_depth) * args.frame_depth   # TS-CAN 需要是 frame_depth 的倍數
    if T == 0:
        raise RuntimeError(f"影片太短：至少要 {args.frame_depth} 影格。")
    x = x[:T]
    x = torch.from_numpy(np.ascontiguousarray(x.transpose(0, 3, 1, 2))).float()  # (T,6,H,W)

    model = TSCAN(frame_depth=args.frame_depth, img_size=args.img_size)
    sd = torch.load(args.weights, map_location="cpu")
    if isinstance(sd, dict) and "state_dict" in sd:      # 有些存法會包一層
        sd = sd["state_dict"]
    sd = {k.replace("module.", ""): v for k, v in sd.items()}  # 去掉 DataParallel 前綴
    model.load_state_dict(sd)   # ← 若這裡報 key/shape 不符，多半是 img_size/frame_depth 沒對齊 config
    model.eval()

    with torch.no_grad():
        bvp = model(x).squeeze().cpu().numpy()   # 每格一個 rPPG/BVP 值

    hr = _calculate_fft_hr(bvp, fs=fps, low_pass=0.75, high_pass=2.5)     # 45–150 bpm
    # RR（近似）：用綠通道平均亮度的『呼吸基線調變』，非深度 RR 模型
    green_mean = roi[:T][..., 1].reshape(T, -1).mean(axis=1)
    rr = fft_rate(green_mean, fps, 0.1, 0.5)     # 6–30 次/分

    print(json.dumps({
        "hr_bpm": round(float(hr), 1),
        "rr_bpm_approx": round(float(rr), 1),   # 近似值；研究級 RR 請改用 BigSmall
        "fps": round(fps, 1),
        "frames_used": int(T),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
