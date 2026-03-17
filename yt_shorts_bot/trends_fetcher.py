"""
YouTube Shorts trend çekici — yt-dlp tabanlı, API anahtarı gerektirmez.
"""
import yt_dlp
import re


CATEGORIES = {
    "Genel Trend":      "ytsearchdate50:#shorts trending",
    "Komedi":           "ytsearchdate30:#shorts komedi funny",
    "Hayvanlar":        "ytsearchdate30:#shorts animals cute",
    "Müzik":            "ytsearchdate30:#shorts music viral",
    "Dans":             "ytsearchdate30:#shorts dance viral",
    "Spor":             "ytsearchdate30:#shorts sport highlights",
    "Yemek":            "ytsearchdate30:#shorts food recipe",
    "Oyun":             "ytsearchdate30:#shorts gaming",
    "Teknoloji":        "ytsearchdate30:#shorts tech",
    "Özel Arama":       None,   # kullanıcı girecek
}


def _is_short(duration):
    """60 saniye veya altı → Short sayılır."""
    return duration is not None and duration <= 60


def fetch_trending(query: str, max_results: int = 20,
                   callback=None) -> list[dict]:
    """
    Verilen sorguya göre YouTube Shorts ara.
    Dönen liste: [{title, url, views, likes, channel, duration, thumbnail}]
    """
    results = []

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "playlistend": max_results * 2,   # filtreleme için fazla çek
    }

    if callback:
        callback(0, 100, f"Aranıyor: {query}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        entries = info.get("entries", []) if info else []

    total = len(entries)
    for i, entry in enumerate(entries):
        if len(results) >= max_results:
            break
        if not entry:
            continue
        dur = entry.get("duration")
        if not _is_short(dur):
            continue

        results.append({
            "title":     entry.get("title", "—"),
            "url":       f"https://youtube.com/shorts/{entry.get('id','')}",
            "views":     entry.get("view_count") or 0,
            "likes":     entry.get("like_count") or 0,
            "channel":   entry.get("uploader") or entry.get("channel") or "—",
            "duration":  dur or 0,
            "id":        entry.get("id", ""),
        })
        if callback:
            pct = int((i + 1) / max(total, 1) * 90)
            callback(pct, 100, f"{len(results)} short bulundu...")

    # İzlenme sayısına göre sırala
    results.sort(key=lambda x: x["views"], reverse=True)

    if callback:
        callback(100, 100, f"Tamamlandı — {len(results)} trend short")

    return results


def fmt_num(n: int) -> str:
    """1_500_000 → 1.5M  gibi kısa gösterim."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)
