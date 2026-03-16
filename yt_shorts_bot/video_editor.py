"""
Video birleştirme + geçiş efektleri (OpenCV tabanlı, PyTorch gerektirmez).
Efektler: fade, slide, zoom, cross-dissolve
"""
import cv2
import numpy as np
from pathlib import Path

TRANSITIONS = ["Fade", "Cross-Dissolve", "Slide Sol→Sağ", "Slide Sağ→Sol", "Zoom"]
DEFAULT_TRANSITION_SEC = 0.5


def _resize_frame(frame: np.ndarray, w: int, h: int) -> np.ndarray:
    if frame.shape[1] != w or frame.shape[0] != h:
        return cv2.resize(frame, (w, h))
    return frame


def _fade(f1: np.ndarray, f2: np.ndarray, t: float) -> np.ndarray:
    """t: 0→1. Önce f1 karaya düşer, sonra f2 aydınlanır."""
    if t < 0.5:
        alpha = 1.0 - t * 2
        return (f1 * alpha).astype(np.uint8)
    else:
        alpha = (t - 0.5) * 2
        return (f2 * alpha).astype(np.uint8)


def _cross_dissolve(f1: np.ndarray, f2: np.ndarray, t: float) -> np.ndarray:
    return cv2.addWeighted(f1, 1.0 - t, f2, t, 0)


def _slide_lr(f1: np.ndarray, f2: np.ndarray, t: float) -> np.ndarray:
    h, w = f1.shape[:2]
    offset = int(w * t)
    canvas = np.zeros_like(f1)
    # f1 sola kayıyor
    if offset < w:
        canvas[:, :w - offset] = f1[:, offset:]
    # f2 sağdan giriyor
    if offset > 0:
        canvas[:, w - offset:] = f2[:, :offset]
    return canvas


def _slide_rl(f1: np.ndarray, f2: np.ndarray, t: float) -> np.ndarray:
    h, w = f1.shape[:2]
    offset = int(w * t)
    canvas = np.zeros_like(f1)
    if offset < w:
        canvas[:, offset:] = f1[:, :w - offset]
    if offset > 0:
        canvas[:, :offset] = f2[:, w - offset:]
    return canvas


def _zoom(f1: np.ndarray, f2: np.ndarray, t: float) -> np.ndarray:
    h, w = f1.shape[:2]
    # f1 büyüyerek çıkıyor
    scale = 1.0 + t * 0.5
    new_w, new_h = int(w * scale), int(h * scale)
    big = cv2.resize(f1, (new_w, new_h))
    x = (new_w - w) // 2
    y = (new_h - h) // 2
    zoomed = big[y:y + h, x:x + w]
    # f2 soluklaşarak giriyor
    return cv2.addWeighted(zoomed, 1.0 - t, f2, t, 0)


EFFECT_FN = {
    "Fade":           _fade,
    "Cross-Dissolve": _cross_dissolve,
    "Slide Sol→Sağ":  _slide_lr,
    "Slide Sağ→Sol":  _slide_rl,
    "Zoom":           _zoom,
}


def _open_cap(path: str):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Video açılamadı: {path}")
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total  = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return cap, fps, width, height, total


def _read_all_frames(path: str, target_w: int, target_h: int,
                     callback=None, base=0, total_frames=1) -> list:
    cap, fps, w, h, n = _open_cap(path)
    frames = []
    while True:
        ret, f = cap.read()
        if not ret:
            break
        frames.append(_resize_frame(f, target_w, target_h))
        if callback and len(frames) % 30 == 0:
            done = base + len(frames)
            callback(done, total_frames, f"Okunuyor: {Path(path).name} ({len(frames)}/{n})")
    cap.release()
    return frames, fps


def merge_videos(video_paths: list, output_path: str,
                 transition: str = "Fade",
                 transition_sec: float = DEFAULT_TRANSITION_SEC,
                 callback=None) -> str:
    if len(video_paths) < 2:
        raise ValueError("En az 2 video gerekli.")

    effect_fn = EFFECT_FN.get(transition, _cross_dissolve)

    # Çıktı boyutunu ilk videodan al
    _, fps0, out_w, out_h, _ = _open_cap(video_paths[0])
    fps = fps0
    trans_frames = max(1, int(fps * transition_sec))

    if callback:
        callback(0, 100, "Videolar okunuyor...")

    # Toplam kare sayısını hesapla (ilerleme çubuğu için)
    total_est = 0
    for p in video_paths:
        c, f, w, h, n = _open_cap(p)
        total_est += n
        c.release()

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out_writer = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

    written = 0

    for idx, path in enumerate(video_paths):
        if callback:
            callback(written, total_est,
                     f"Video {idx+1}/{len(video_paths)} okunuyor: {Path(path).name}")

        frames, _ = _read_all_frames(path, out_w, out_h,
                                     callback=callback,
                                     base=written,
                                     total_frames=total_est)

        if idx == 0:
            # İlk video: tamamını yaz (geçiş payı hariç)
            for f in frames[:-trans_frames] if len(frames) > trans_frames else frames:
                out_writer.write(f)
                written += 1
            prev_tail = frames[-trans_frames:] if len(frames) >= trans_frames else frames
        else:
            # Geçiş efekti: önceki videonun sonu + bu videonun başı
            curr_head = frames[:trans_frames] if len(frames) >= trans_frames else frames
            n_trans = min(len(prev_tail), len(curr_head))

            if callback:
                callback(written, total_est,
                         f"Geçiş efekti uygulanıyor: {transition} ({n_trans} kare)")

            for t_idx in range(n_trans):
                t = t_idx / max(n_trans - 1, 1)
                blend = effect_fn(prev_tail[t_idx], curr_head[t_idx], t)
                out_writer.write(blend)
                written += 1

            # Geri kalan kareler
            rest = frames[trans_frames:] if len(frames) > trans_frames else []
            # Son video değilse kuyruk payını ayır
            if idx < len(video_paths) - 1 and len(rest) > trans_frames:
                for f in rest[:-trans_frames]:
                    out_writer.write(f)
                    written += 1
                prev_tail = rest[-trans_frames:]
            else:
                for f in rest:
                    out_writer.write(f)
                    written += 1
                prev_tail = frames[-trans_frames:] if len(frames) >= trans_frames else frames

        if callback:
            callback(written, total_est,
                     f"{idx+1}/{len(video_paths)} video eklendi")

    out_writer.release()

    if callback:
        callback(total_est, total_est, f"Tamamlandı → {output_path}")

    return output_path
