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


def _get_ffmpeg_path() -> str:
    import shutil
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        try:
            import imageio_ffmpeg
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError:
            pass
    return ffmpeg or ""


def download_youtube_audio(url: str, out_dir: str, callback=None) -> str:
    """YouTube URL'den sadece ses indir. mp3 olarak döner."""
    import yt_dlp
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ffmpeg_path = _get_ffmpeg_path()
    outtmpl = str(out_dir / "%(title).60s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    if ffmpeg_path:
        import os
        ydl_opts["ffmpeg_location"] = ffmpeg_path

    if callback:
        callback(0, 100, "YouTube'dan ses indiriliyor...")

    final_path = []

    def progress_hook(d):
        if d["status"] == "downloading" and callback:
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            downloaded = d.get("downloaded_bytes", 0)
            pct = int(downloaded / total * 80)
            callback(pct, 100, f"İndiriliyor... {d.get('_percent_str','').strip()}")
        elif d["status"] == "finished":
            final_path.append(d.get("filename", ""))

    ydl_opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    if callback:
        callback(85, 100, "Ses dönüştürülüyor (mp3)...")

    # En son indirilen mp3'ü bul
    candidates = sorted(out_dir.glob("*.mp3"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not candidates:
        # mp3 yoksa herhangi bir ses dosyasını dene
        for ext in ("*.webm", "*.m4a", "*.opus", "*.ogg"):
            candidates = sorted(out_dir.glob(ext), key=lambda f: f.stat().st_mtime, reverse=True)
            if candidates:
                break
    if not candidates:
        raise RuntimeError("Ses dosyası oluşturulamadı. ffmpeg kurulu mu?")

    audio_path = str(candidates[0])

    if callback:
        callback(100, 100, f"Ses indirildi → {audio_path}")

    return audio_path


def _get_duration(ffmpeg: str, path: str) -> float:
    """ffmpeg ile dosya süresini saniye cinsinden döner."""
    import subprocess, re
    result = subprocess.run(
        [ffmpeg, "-i", path],
        capture_output=True, text=True)
    match = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", result.stderr)
    if match:
        h, m, s = int(match.group(1)), int(match.group(2)), float(match.group(3))
        return h * 3600 + m * 60 + s
    return 0.0


def add_audio_to_video(video_path: str, audio_path: str, output_path: str,
                       volume: float = 1.0, loop_audio: bool = True,
                       callback=None) -> str:
    """Videoya ses ekle. WhatsApp/sosyal medya uyumlu H.264+AAC MP4 üretir."""
    import subprocess, tempfile, math, os

    ffmpeg = _get_ffmpeg_path()
    if not ffmpeg:
        raise RuntimeError("ffmpeg bulunamadı. 'pip install imageio-ffmpeg' ile yükleyin.")

    if callback:
        callback(5, 100, "Video süresi hesaplanıyor...")

    video_dur = _get_duration(ffmpeg, video_path)
    audio_dur = _get_duration(ffmpeg, audio_path)

    # Döngü sayısını hesapla (ses videodan kısaysa)
    loop_count = 0
    if loop_audio and audio_dur > 0 and video_dur > 0:
        loop_count = max(0, math.ceil(video_dur / audio_dur) - 1)

    if callback:
        callback(15, 100, f"Ses hazırlanıyor (döngü: {loop_count}x)...")

    # Adım 1: Sesi döngüye al ve normalize et (geçici dosyaya)
    with tempfile.TemporaryDirectory() as td:
        looped_audio = os.path.join(td, "looped.wav")

        # -stream_loop ile tam sayıda döngü → kesintisiz ses
        # loudnorm: EBU R128 normalizasyon — kliplenmeyi önler
        loop_cmd = [
            ffmpeg, "-y",
            "-stream_loop", str(loop_count),
            "-i", audio_path,
            "-af", (
                f"aresample=44100,"
                f"loudnorm=I=-16:TP=-1.5:LRA=11,"
                f"volume={volume}"
            ),
            "-ac", "2",
            "-ar", "44100",
            "-sample_fmt", "s16",
            looped_audio,
        ]
        r = subprocess.run(loop_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"Ses hazırlama hatası:\n{r.stderr[-600:]}")

        if callback:
            callback(40, 100, "Ses videoya ekleniyor (H.264 kodlanıyor)...")

        # Adım 2: Video + hazır ses → H.264 MP4
        mix_cmd = [
            ffmpeg, "-y",
            "-i", video_path,
            "-i", looped_audio,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.1",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-ar", "44100",
            "-shortest",
            output_path,
        ]
        r2 = subprocess.run(mix_cmd, capture_output=True, text=True)
        if r2.returncode != 0:
            raise RuntimeError(f"ffmpeg hatası:\n{r2.stderr[-800:]}")

    if callback:
        callback(100, 100, f"Tamamlandı → {output_path}")

    return output_path
