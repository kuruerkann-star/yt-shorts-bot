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

    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg_path = "ffmpeg"

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_template = str(Path(output_dir) / "%(title).40s.%(ext)s")

    ydl_opts = {
        "outtmpl": out_template,
        "format": (
            "bestvideo[height<=1080][ext=mp4][vcodec!*=av01][vcodec!*=av1]"
            "+bestaudio[ext=m4a]"
            "/bestvideo[height<=1080][ext=mp4]+bestaudio"
            "/best[height<=1080][ext=mp4]"
            "/best[height<=1080]"
            "/best"
        ),
        "quiet": True,
        "no_warnings": True,
        "ffmpeg_location": ffmpeg_path,
        "merge_output_format": "mp4",
    }

    downloaded_path = [None]

    def progress_hook(d):
        if d["status"] == "downloading" and callback:
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            done  = d.get("downloaded_bytes", 0)
            pct   = int(done / total * 50)
            callback(pct, 100, f"İndiriliyor... {pct*2}%")

    ydl_opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        expected = ydl.prepare_filename(info)

    base = os.path.splitext(expected)[0]
    for ext in [".mp4", ".mkv", ".webm"]:
        candidate = base + ext
        if os.path.exists(candidate):
            return candidate

    if os.path.exists(expected):
        return expected

    for f in sorted(Path(output_dir).glob(f"{Path(base).name}*"),
                    key=lambda p: p.stat().st_mtime, reverse=True):
        if f.suffix in (".mp4", ".mkv", ".webm"):
            return str(f)

    raise FileNotFoundError(f"İndirilen video dosyası bulunamadi: {base}")


# COCO sinif id -> isim (hayvanlar)
COCO_ANIMALS = {
    14: "bird", 15: "cat", 16: "dog", 17: "horse",
    18: "sheep", 19: "cow", 20: "elephant", 21: "bear",
    22: "zebra", 23: "giraffe",
}

SOURCE_ANIMALS = {
    "Kedi":     [15],
    "Köpek":    [16],
    "Kuş":      [14],
    "At":       [17],
    "Ayı":      [21],
    "Tüm Hayvanlar": list(COCO_ANIMALS.keys()),
}


def replace_animal(input_path: str, output_path: str,
                   source_animal: str, target_animal: str,
                   confidence: float = 0.20,
                   callback=None) -> str:
    """
    Kare farkı ile hareketli nesneyi tespit edip hedef hayvanla değiştirir.
    Hafıza dostu — PyTorch/YOLO gerektirmez.
    """
    from animal_overlays import overlay_animal_on_frame
    import sys

    def log(msg):
        if callback:
            callback(0, 1, msg)
        print(msg, flush=True)

    log("Video açılıyor...")

    cap = cv2.VideoCapture(input_path)
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    log(f"Video: {width}x{height}, {total} kare, {fps:.0f}fps")

    # Islem icin kucuk boyut
    pw = min(width,  640)
    ph = int(height * pw / width)
    sx = width  / pw
    sy = height / ph

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_w  = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    ret, prev = cap.read()
    if not ret:
        cap.release(); out_w.release()
        raise RuntimeError("Video okunamadı.")
    prev_small = cv2.cvtColor(cv2.resize(prev, (pw, ph)), cv2.COLOR_BGR2GRAY)

    i = 1
    found = 0
    out_w.write(prev)  # ilk kare degismeden

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small = cv2.resize(frame, (pw, ph))
        gray  = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        # Kare farki
        diff = cv2.absdiff(gray, prev_small)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE,
                 cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN,
                 cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = pw * ph * 0.015
        big = [c for c in contours if cv2.contourArea(c) > min_area]

        detections = []
        if big:
            biggest = max(big, key=cv2.contourArea)
            bx, by, bw, bh = cv2.boundingRect(biggest)
            x1 = int(bx*sx);       y1 = int(by*sy)
            x2 = int((bx+bw)*sx);  y2 = int((by+bh)*sy)
            mask_s = np.zeros((ph, pw), dtype=np.float32)
            cv2.drawContours(mask_s, [biggest], -1, 1.0, -1)
            mask_full = cv2.resize(mask_s, (width, height), interpolation=cv2.INTER_LINEAR)
            detections.append((x1, y1, x2, y2, mask_full))
            found += 1

        if detections:
            frame = overlay_animal_on_frame(frame, detections, target_animal, i)

        out_w.write(frame)
        prev_small = gray
        i += 1
        if callback and i % 30 == 0:
            callback(i, total, f"Kare {i}/{total} | {found} değiştirildi")

    cap.release()
    out_w.release()

    if callback:
        callback(total, total, f"Tamamlandı! {found} karede hayvan değiştirildi.")
    return output_path
