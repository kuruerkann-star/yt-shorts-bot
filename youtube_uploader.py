import os
import pickle
import json
from pathlib import Path
from typing import Dict, Optional

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = "token.pickle"


class YouTubeUploader:
    def __init__(self, client_secrets_file: str):
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self._load_credentials()

    def _load_credentials(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "rb") as f:
                    self.credentials = pickle.load(f)
            except Exception:
                self.credentials = None

    def _save_credentials(self):
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(self.credentials, f)

    def authenticate(self) -> bool:
        if self.credentials and self.credentials.valid:
            return True

        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build
        except ImportError:
            raise ImportError(
                "Google API kutuphaneleri yuklu degil.\n"
                "Lutfen sunlari calistirin:\n"
                "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            )

        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            try:
                from google.auth.transport.requests import Request
                self.credentials.refresh(Request())
                self._save_credentials()
                return True
            except Exception:
                self.credentials = None

        if not os.path.exists(self.client_secrets_file):
            raise FileNotFoundError(
                f"Client secrets dosyasi bulunamadi: {self.client_secrets_file}\n"
                "Google Cloud Console'dan OAuth 2.0 kimlik bilgilerini indirin."
            )

        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
        self.credentials = flow.run_local_server(port=0)
        self._save_credentials()
        return True

    def upload_short(self, video_path: str, title: str, description: str,
                     tags: list = None, category_id: str = "22",
                     privacy: str = "public", callback=None) -> Optional[str]:
        if not self.credentials or not self.credentials.valid:
            self.authenticate()

        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
        except ImportError:
            raise ImportError("google-api-python-client yuklu degil.")

        youtube = build("youtube", "v3", credentials=self.credentials)

        if not description.endswith("#Shorts"):
            description = description + "\n\n#Shorts"

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": (tags or []) + ["Shorts", "shorts", "viral"],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(video_path, chunksize=1024 * 1024,
                                resumable=True, mimetype="video/mp4")

        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status and callback:
                callback(int(status.progress() * 100))

        video_id = response.get("id", "")
        if callback:
            callback(100)
        return f"https://www.youtube.com/shorts/{video_id}" if video_id else None

    def is_authenticated(self) -> bool:
        return self.credentials is not None and self.credentials.valid
