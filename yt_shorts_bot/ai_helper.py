import json
from typing import Dict, Optional


SYSTEM_PROMPT = (
    "Sen bir YouTube Shorts video scripti uzmanisın. "
    "Asagida sana bir referans trendin bilgileri verilecek. "
    "Bu trendi analiz et: neden viral olmus, hangi duygulara hitap ediyor, hangi kitleyi cekmis? "
    "Sonra bu analizi kullanarak kullanicinin istedigi konuda benzer tarzda, "
    "viral potansiyelli OZGUN bir Shorts videosu icin Turkce icerik olustur. "
    "Referansi kopyalama, ilham al. "
    "Ciktin MUTLAKA asagidaki saf JSON formatinda olmali, baska hicbir sey yazma:\n"
    "{\n"
    '  "title": "Video basligi (max 80 karakter, dikkat cekici)",\n'
    '  "content_lines": ["Guc satiri 1", "Satir 2", "Satir 3", "Satir 4", "Satir 5", "Satir 6"],\n'
    '  "hashtags": "#shorts #viral #trend ...",\n'
    '  "description": "YouTube aciklama metni (SEO dostu)"\n'
    "}"
)

class AIHelper:
    def __init__(self, provider: str = "grok", api_key: str = "", **_):
        self.provider = provider.lower()
        self.api_key = api_key

    def generate_video_content(self, prompt: str,
                                video_context: Optional[Dict] = None) -> Dict:
        full_prompt = self._build_prompt(prompt, video_context)
        return self._call_grok(full_prompt)

    def _build_prompt(self, user_prompt: str,
                      video_context: Optional[Dict]) -> str:
        parts = []
        if video_context:
            parts.append("=== REFERANS TREND VIDEO ===")
            parts.append(f"Baslik      : {video_context.get('title', '-')}")
            parts.append(f"Kanal       : {video_context.get('channel', '-')}")
            parts.append(f"Izlenme     : {video_context.get('view_count', 0):,}")
            parts.append(f"Begeni      : {video_context.get('like_count', 0):,}")
            tags = video_context.get("tags", [])
            if tags:
                parts.append(f"Etiketler   : {', '.join(tags[:10])}")
            desc = video_context.get("description", "").strip()
            if desc:
                parts.append(f"Aciklama    : {desc[:300]}")
            parts.append("=== KULLANICI ISTEGI ===")
        parts.append(user_prompt)
        return "\n".join(parts)

    def _call_grok(self, prompt: str) -> Dict:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai paketi yuklu degil. 'pip install openai' calistirin.")

        if not self.api_key:
            raise ValueError("Grok API anahtari eksik. console.x.ai adresinden alin.")

        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.x.ai/v1",
            )
            response = client.chat.completions.create(
                model="grok-3-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.85,
                max_tokens=700,
            )
            return self._parse_response(response.choices[0].message.content.strip())
        except Exception as e:
            err = str(e)
            if "401" in err or "invalid" in err.lower():
                raise ValueError("Grok API anahtari gecersiz. console.x.ai adresinden kontrol edin.")
            if "429" in err:
                raise ValueError("Grok kota asimi (429). Biraz bekleyin.")
            raise

    def _parse_response(self, raw: str) -> Dict:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError(f"AI gecerli JSON dondurmedi.\nYanit: {raw[:200]}")
        data = json.loads(raw[start:end])
        for key in ["title", "content_lines", "hashtags", "description"]:
            if key not in data:
                raise ValueError(f"AI yanitinda '{key}' alani eksik.")
        return data

    def is_configured(self) -> bool:
        return bool(self.api_key.strip())
