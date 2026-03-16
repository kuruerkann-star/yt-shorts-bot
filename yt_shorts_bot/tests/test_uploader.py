import sys
import os
import pickle
import tempfile
import unittest
from unittest.mock import patch, MagicMock, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestIsAuthenticated(unittest.TestCase):
    def _make_uploader(self, tmpdir, creds=None):
        secrets_path = os.path.join(tmpdir, "client_secret.json")
        with open(secrets_path, "w") as f:
            f.write("{}")
        token_path = os.path.join(tmpdir, "token.pickle")

        with patch("youtube_uploader.TOKEN_FILE", token_path):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader(secrets_path)
            uploader.credentials = creds
        return uploader

    def test_is_authenticated_false_no_credentials(self):
        tmpdir = tempfile.mkdtemp()
        with patch("youtube_uploader.TOKEN_FILE", os.path.join(tmpdir, "token.pickle")):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = None
            self.assertFalse(uploader.is_authenticated())

    def test_is_authenticated_true(self):
        mock_creds = MagicMock()
        mock_creds.valid = True
        with patch("youtube_uploader.TOKEN_FILE", "/nonexistent/token.pickle"):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = mock_creds
            self.assertTrue(uploader.is_authenticated())

    def test_is_authenticated_false_invalid_credentials(self):
        mock_creds = MagicMock()
        mock_creds.valid = False
        with patch("youtube_uploader.TOKEN_FILE", "/nonexistent/token.pickle"):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = mock_creds
            self.assertFalse(uploader.is_authenticated())


class TestLoadCredentials(unittest.TestCase):
    def test_load_credentials_missing_file(self):
        tmpdir = tempfile.mkdtemp()
        token_path = os.path.join(tmpdir, "no_token.pickle")
        with patch("youtube_uploader.TOKEN_FILE", token_path):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = None
            uploader._load_credentials()
            self.assertIsNone(uploader.credentials)

    def test_load_credentials_corrupt_file(self):
        tmpdir = tempfile.mkdtemp()
        token_path = os.path.join(tmpdir, "corrupt.pickle")
        with open(token_path, "wb") as f:
            f.write(b"not valid pickle data!!!!")
        with patch("youtube_uploader.TOKEN_FILE", token_path):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = None
            uploader._load_credentials()
            self.assertIsNone(uploader.credentials)

    def test_load_credentials_valid_file(self):
        import io
        tmpdir = tempfile.mkdtemp()
        token_path = os.path.join(tmpdir, "token.pickle")
        sentinel = object()
        with open(token_path, "wb") as f:
            pickle.dump(sentinel, f)
        with patch("youtube_uploader.TOKEN_FILE", token_path):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = None
            uploader._load_credentials()
            self.assertIsNotNone(uploader.credentials)


class TestAuthenticate(unittest.TestCase):
    def test_authenticate_missing_secrets_raises(self):
        tmpdir = tempfile.mkdtemp()
        token_path = os.path.join(tmpdir, "token.pickle")
        with patch("youtube_uploader.TOKEN_FILE", token_path):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = None
            uploader.client_secrets_file = os.path.join(tmpdir, "nonexistent.json")

            with self.assertRaises((FileNotFoundError, ImportError)):
                uploader.authenticate()

    def test_authenticate_already_valid_returns_true(self):
        mock_creds = MagicMock()
        mock_creds.valid = True
        with patch("youtube_uploader.TOKEN_FILE", "/nonexistent/token.pickle"):
            from youtube_uploader import YouTubeUploader
            uploader = YouTubeUploader.__new__(YouTubeUploader)
            uploader.credentials = mock_creds
            uploader.client_secrets_file = "dummy.json"
            result = uploader.authenticate()
            self.assertTrue(result)


class TestUploadShortCallsAuth(unittest.TestCase):
    def test_upload_short_no_credentials_calls_auth(self):
        tmpdir = tempfile.mkdtemp()
        token_path = os.path.join(tmpdir, "token.pickle")
        dummy_video = os.path.join(tmpdir, "video.mp4")
        with open(dummy_video, "wb") as f:
            f.write(b"\x00" * 100)

        mock_build = MagicMock()
        mock_youtube = MagicMock()
        mock_request = MagicMock()
        mock_request.next_chunk.return_value = (None, {"id": "fake_vid_id"})
        mock_youtube.videos.return_value.insert.return_value = mock_request
        mock_build.return_value = mock_youtube

        mock_googleapi = MagicMock()
        mock_googleapi.discovery.build = mock_build
        mock_mediaupload = MagicMock()
        mock_googleapi.http.MediaFileUpload = mock_mediaupload

        modules_to_patch = {
            "googleapiclient": mock_googleapi,
            "googleapiclient.discovery": mock_googleapi.discovery,
            "googleapiclient.http": mock_googleapi.http,
        }

        with patch("youtube_uploader.TOKEN_FILE", token_path):
            with patch.dict("sys.modules", modules_to_patch):
                from youtube_uploader import YouTubeUploader
                uploader = YouTubeUploader.__new__(YouTubeUploader)
                uploader.credentials = None
                uploader.client_secrets_file = "dummy.json"

                with patch.object(uploader, "authenticate") as mock_auth:
                    mock_auth.side_effect = lambda: setattr(
                        uploader, "credentials", MagicMock(valid=True)
                    )
                    uploader.upload_short(
                        video_path=dummy_video,
                        title="Test",
                        description="Desc",
                    )
                    mock_auth.assert_called_once()

        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
