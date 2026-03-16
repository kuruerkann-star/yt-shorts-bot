import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from youtube_api import YouTubeAPI


def _make_search_response(video_ids):
    return {
        "items": [
            {"id": {"videoId": vid}} for vid in video_ids
        ]
    }


def _make_videos_response(items):
    return {"items": items}


def _video_item(vid_id, title, view_count, like_count=0, tags=None, duration="PT55S"):
    return {
        "id": vid_id,
        "contentDetails": {"duration": duration},
        "snippet": {
            "title": title,
            "description": "desc",
            "channelTitle": "TestChannel",
            "tags": tags or [],
            "thumbnails": {"high": {"url": "http://img.jpg"}},
            "categoryId": "22",
            "publishedAt": "2026-01-01T00:00:00Z",
        },
        "statistics": {
            "viewCount": str(view_count),
            "likeCount": str(like_count),
            "commentCount": "0",
        },
    }


class TestYouTubeAPISearch(unittest.TestCase):
    def setUp(self):
        self.api = YouTubeAPI("FAKE_KEY")

    @patch("youtube_api.requests.get")
    def test_search_returns_sorted_by_views(self, mock_get):
        search_resp = MagicMock()
        search_resp.raise_for_status = MagicMock()
        search_resp.json.return_value = _make_search_response(["vid1", "vid2"])

        details_resp = MagicMock()
        details_resp.raise_for_status = MagicMock()
        details_resp.json.return_value = _make_videos_response([
            _video_item("vid1", "Low Views", 100),
            _video_item("vid2", "High Views", 99999),
        ])

        mock_get.side_effect = [search_resp, details_resp]
        results = self.api.search_trending_shorts(query="test")

        self.assertEqual(results[0]["title"], "High Views")
        self.assertEqual(results[1]["title"], "Low Views")

    @patch("youtube_api.requests.get")
    def test_search_empty_query_adds_shorts_tag(self, mock_get):
        search_resp = MagicMock()
        search_resp.raise_for_status = MagicMock()
        search_resp.json.return_value = _make_search_response([])
        mock_get.return_value = search_resp

        self.api.search_trending_shorts(query="")

        call_params = mock_get.call_args[1]["params"]
        self.assertIn("#shorts", call_params.get("q", ""))

    @patch("youtube_api.requests.get")
    def test_search_http_error_raises(self, mock_get):
        import requests as req
        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = req.exceptions.HTTPError("403")
        mock_get.return_value = mock_resp

        with self.assertRaises(Exception) as ctx:
            self.api.search_trending_shorts(query="test")
        self.assertIn("Arama hatasi", str(ctx.exception))

    @patch("youtube_api.requests.get")
    def test_get_video_details_parses_correctly(self, mock_get):
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = _make_videos_response([
            _video_item("abc123", "My Short", 5000, like_count=200)
        ])
        mock_get.return_value = resp

        results = self.api.get_video_details(["abc123"])
        self.assertEqual(len(results), 1)
        r = results[0]
        self.assertEqual(r["id"], "abc123")
        self.assertEqual(r["title"], "My Short")
        self.assertEqual(r["view_count"], 5000)
        self.assertEqual(r["like_count"], 200)
        self.assertEqual(r["url"], "https://www.youtube.com/shorts/abc123")

    @patch("youtube_api.requests.get")
    def test_get_video_details_missing_stats(self, mock_get):
        item = _video_item("x1", "No Stats", 0)
        item["statistics"] = {}
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        resp.json.return_value = _make_videos_response([item])
        mock_get.return_value = resp

        results = self.api.get_video_details(["x1"])
        self.assertEqual(results[0]["view_count"], 0)
        self.assertEqual(results[0]["like_count"], 0)
        self.assertEqual(results[0]["comment_count"], 0)


class TestIsShort(unittest.TestCase):
    def setUp(self):
        self.api = YouTubeAPI("key")

    def test_is_short_true(self):
        self.assertTrue(self.api._is_short("PT55S"))

    def test_is_short_exactly_60(self):
        self.assertTrue(self.api._is_short("PT60S"))

    def test_is_short_false_long(self):
        self.assertFalse(self.api._is_short("PT2M10S"))

    def test_is_short_empty_string(self):
        self.assertFalse(self.api._is_short(""))


if __name__ == "__main__":
    unittest.main()
