import json
from typing import Dict, Optional


SYSTEM_PROMPT = (
    "Sen bir YouTube Shorts video scripti yazarısın. "
    "Kullanicinin istedigi konuda viral, ilgi cekici ve kısa bir Shorts videosu icin icerik uretiyorsun. "
    "Her zaman Turkce yanit ver. "
    "Ciktin mutlaka asagidaki JSON formatinda olmali, baska hicbir sey yazma:\n"
    "{\n"
    '  "title": "Video basligi (max 80 karakter)",\n'
    '  "content_lines": ["Satir 1", "Satir 2", "Satir 3", "Satir 4", "Satir 5", "Satir 6"],\n'
    '  "hashtags": "#shorts #viral #trend ...",\n'
    '  "description": "YouTube aciklama metni"\n'
    "}"
)


class AIHelper:
    def __init__(self, provider: str = "openai", api_key: str = ""):
        self.provider = provider.lower()
        self.api_key = api_key

    def generate_video_content(self, prompt: str, language: str = "tr") -> Dict:
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "gemini":
            return self._call_gemini(prompt)
        else:
            raise ValueError(f"Desteklenmeyen AI saglayici: {self.provider}")

    def _call_openai(self, prompt: str) -> Dict:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai paketi yuklu degil. 'pip install openai' calistirin.")

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.85,
            max_tokens=600,
        )
        raw = response.choices[0].message.content.strip()
        return self._parse_response(raw)

    def _call_gemini(self, prompt: str) -> Dict:
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai paketi yuklu degil. "
                "'pip install google-genai' calistirin."
            )

        client = genai.Client(api_key=self.api_key)
        full_prompt = SYSTEM_PROMPT + "\n\nKullanici istegi: " + prompt
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
        )
        raw = response.text.strip()
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> Dict:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("AI gecerli bir JSON dondurmedi.")
        json_str = raw[start:end]
        data = json.loads(json_str)
        required = ["title", "content_lines", "hashtags", "description"]
        for key in required:
            if key not in data:
                raise ValueError(f"AI yanitinda '{key}' alani eksik.")
        return data

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())
