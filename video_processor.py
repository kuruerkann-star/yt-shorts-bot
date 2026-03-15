import os
import cv2
import numpy as np
from pathlib import Path


ANIMAL_COLORS = {
    "Turuncu Kedi":   [(5,  100, 80),  (22, 255, 255)],
    "Gri Kedi":       [(0,  0,   60),  (180, 40,  200)],
    "Kahverengi Köpek": [(10, 60, 40),  (20, 200, 180)],
    "Sarı/Krem":      [(22, 50,  100), (35, 220, 255)],
    "Beyaz Hayvan":   [(0,  0,   180), (180, 40,  255)],
    "Siyah Hayvan":   [(0,  0,   0),   (180, 255, 60)],
}

TARGET_COLORS = {
    "Mavi":     (120, 200, 200),
    "Yeşil":    (60,  200, 200),
    "Kırmızı":  (0,   220, 220),
    "Mor":      (140, 200, 200),
    "Pembe":    (160, 180, 220),
    "Cyan":     (90,  220, 220),
    "Sarı":     (28,  230, 230),
    "Turuncu":  (12,  230, 230),
}


def _shift_hue(frame_bgr: np.ndarray,
               lower: tuple, upper: tuple,
               target_hsv: tuple,
               sensitivity: int = 15) -> np.ndarray:
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    lo = np.array([max(0, lower[0] - sensitivity), lower[1], lower[2]], np.uint8)
    hi = np.array([min(180, upper[0] + sensitivity), upper[1], upper[2]], np.uint8)

    if lower[0] == 0 and upper[0] == 180:
        mask = cv2.inRange(hsv, np.array([0, lower[1], lower[2]], np.uint8),
                           np.array([180, upper[1], upper[2]], np.uint8))
    else:
        mask = cv2.inRange(hsv, lo, hi)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    mask = cv2.dilate(mask, None, iterations=2)

    result = hsv.copy()
    result[mask > 0, 0] = target_hsv[0]
    result[mask > 0, 1] = np.clip(result[mask > 0, 1] * 1.1, 0, 255).astype(np.uint8)
    result[mask > 0, 2] = np.clip(result[mask > 0, 2] * 1.05, 0, 255).astype(np.uint8)

    return cv2.cvtColor(result, cv2.COLOR_HSV2BGR)


def process_video(input_path: str, output_path: str,
                  animal_color: str, target_color: str,
                  sensitivity: int = 15,
                  callback=None) -> str:
    lower, upper = ANIMAL_COLORS[animal_color]
    t_hsv = TARGET_COLORS[target_color]

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    i = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        processed = _shift_hue(frame, lower, upper, t_hsv, sensitivity)
        out.write(processed)
        i += 1
        if callback and i % 30 == 0:
            callback(i, total, f"Kare {i}/{total} isleniyor...")

    cap.release()
    out.release()

    if callback:
        callback(total, total, "Video tamamlandi!")

    return output_path


def download_video(url: str, output_dir: str, callback=None) -> str:
    try:
        import yt_dlp
    except ImportError:
        raise ImportError("yt-dlp yuklu degil. 'pip install yt-dlp' calistirin.")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_template = str(Path(output_dir) / "%(title).40s.%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "quiet": True,
        "no_warnings": True,
    }

    downloaded_path = [None]

    def progress_hook(d):
        if d["status"] == "downloading" and callback:
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            done  = d.get("downloaded_bytes", 0)
            pct   = int(done / total * 50)
            callback(pct, 100, f"İndiriliyor... {pct*2}%")
        elif d["status"] == "finished":
            downloaded_path[0] = d["filename"]

    ydl_opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if downloaded_path[0] is None:
            downloaded_path[0] = ydl.prepare_filename(info)

    path = downloaded_path[0]
    if not path.endswith(".mp4"):
        mp4 = path.rsplit(".", 1)[0] + ".mp4"
        if os.path.exists(mp4):
            path = mp4

    return path
