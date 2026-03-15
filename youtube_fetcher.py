from typing import Dict


class YouTubeFetcher:
    def get_video_info(self, url: str) -> Dict:
        try:
            import yt_dlp
        except ImportError:
            raise ImportError("yt-dlp yuklu degil. 'pip install yt-dlp' calistirin.")

        opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title", ""),
            "description": (info.get("description") or "")[:500],
            "tags": info.get("tags") or [],
            "view_count": info.get("view_count") or 0,
            "like_count": info.get("like_count") or 0,
            "channel": info.get("uploader") or info.get("channel") or "",
            "duration": info.get("duration") or 0,
            "url": url,
        }
