import os
import json
import requests
from typing import List, Dict, Optional


class YouTubeAPI:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_trending_shorts(self, query: str = "", max_results: int = 10,
                                region_code: str = "TR", language: str = "tr") -> List[Dict]:
        params = {
            "part": "snippet",
            "type": "video",
            "videoDuration": "short",
            "order": "viewCount",
            "maxResults": max_results,
            "key": self.api_key,
            "regionCode": region_code,
            "relevanceLanguage": language,
        }
        if query:
            params["q"] = query + " #shorts"
        else:
            params["q"] = "#shorts"

        try:
            response = requests.get(f"{self.BASE_URL}/search", params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            video_ids = [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]
            if not video_ids:
                return []
            details = self.get_video_details(video_ids)
            return details
        except Exception as e:
            raise Exception(f"Arama hatasi: {str(e)}")

    def get_video_details(self, video_ids: List[str]) -> List[Dict]:
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(video_ids),
            "key": self.api_key,
        }
        try:
            response = requests.get(f"{self.BASE_URL}/videos", params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                results.append({
                    "id": item["id"],
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "tags": snippet.get("tags", []),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                    "view_count": int(stats.get("viewCount", 0)),
                    "like_count": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "url": f"https://www.youtube.com/shorts/{item['id']}",
                    "category_id": snippet.get("categoryId", ""),
                    "published_at": snippet.get("publishedAt", ""),
                })
            results.sort(key=lambda x: x["view_count"], reverse=True)
            return results
        except Exception as e:
            raise Exception(f"Video detay hatasi: {str(e)}")

    def get_trending_videos(self, region_code: str = "TR", max_results: int = 10) -> List[Dict]:
        params = {
            "part": "snippet,statistics,contentDetails",
            "chart": "mostPopular",
            "regionCode": region_code,
            "maxResults": 50,
            "key": self.api_key,
            "videoCategoryId": "",
        }
        try:
            response = requests.get(f"{self.BASE_URL}/videos", params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            results = []
            for item in data.get("items", []):
                duration = item.get("contentDetails", {}).get("duration", "")
                if self._is_short(duration):
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    results.append({
                        "id": item["id"],
                        "title": snippet.get("title", ""),
                        "description": snippet.get("description", ""),
                        "channel": snippet.get("channelTitle", ""),
                        "tags": snippet.get("tags", []),
                        "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                        "view_count": int(stats.get("viewCount", 0)),
                        "like_count": int(stats.get("likeCount", 0)),
                        "comment_count": int(stats.get("commentCount", 0)),
                        "url": f"https://www.youtube.com/shorts/{item['id']}",
                        "published_at": snippet.get("publishedAt", ""),
                    })
            results.sort(key=lambda x: x["view_count"], reverse=True)
            return results[:max_results]
        except Exception as e:
            raise Exception(f"Trend video hatasi: {str(e)}")

    def _is_short(self, duration: str) -> bool:
        import re
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
        if not match:
            return False
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds <= 60
