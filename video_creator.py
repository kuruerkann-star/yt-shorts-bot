import os
import random
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np


VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

COLOR_THEMES = [
    {"bg": (15, 15, 35), "accent": (255, 60, 120), "text": (255, 255, 255), "sub": (200, 200, 220)},
    {"bg": (10, 25, 10), "accent": (0, 230, 100), "text": (255, 255, 255), "sub": (180, 220, 180)},
    {"bg": (25, 10, 10), "accent": (255, 100, 0), "text": (255, 255, 255), "sub": (220, 180, 160)},
    {"bg": (10, 10, 40), "accent": (80, 120, 255), "text": (255, 255, 255), "sub": (180, 190, 240)},
    {"bg": (30, 0, 40), "accent": (220, 0, 255), "text": (255, 255, 255), "sub": (220, 180, 230)},
    {"bg": (40, 30, 0), "accent": (255, 200, 0), "text": (255, 255, 255), "sub": (230, 220, 170)},
]


class VideoCreator:
    def __init__(self, output_dir: str = "output_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.font_paths = self._find_fonts()

    def _find_fonts(self) -> Dict[str, Optional[str]]:
        candidates = {
            "bold": [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/calibrib.ttf",
                "C:/Windows/Fonts/verdanab.ttf",
                "C:/Windows/Fonts/trebucbd.ttf",
            ],
            "regular": [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "C:/Windows/Fonts/verdana.ttf",
            ],
        }
        found = {}
        for style, paths in candidates.items():
            for p in paths:
                if os.path.exists(p):
                    found[style] = p
                    break
            else:
                found[style] = None
        return found

    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        key = "bold" if bold else "regular"
        path = self.font_paths.get(key)
        try:
            if path:
                return ImageFont.truetype(path, size)
        except Exception:
            pass
        return ImageFont.load_default()

    def _draw_gradient_bg(self, draw: ImageDraw.Draw, theme: Dict) -> None:
        bg = theme["bg"]
        accent = theme["accent"]
        for y in range(VIDEO_HEIGHT):
            ratio = y / VIDEO_HEIGHT
            r = int(bg[0] + (accent[0] - bg[0]) * ratio * 0.15)
            g = int(bg[1] + (accent[1] - bg[1]) * ratio * 0.15)
            b = int(bg[2] + (accent[2] - bg[2]) * ratio * 0.15)
            draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))

    def _draw_decorations(self, draw: ImageDraw.Draw, theme: Dict) -> None:
        accent = theme["accent"]
        for _ in range(6):
            x = random.randint(0, VIDEO_WIDTH)
            y = random.randint(0, VIDEO_HEIGHT)
            r = random.randint(80, 300)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         outline=accent + (30,), width=2)
        draw.rectangle([0, 0, VIDEO_WIDTH, 8], fill=accent)
        draw.rectangle([0, VIDEO_HEIGHT - 8, VIDEO_WIDTH, VIDEO_HEIGHT], fill=accent)

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont,
                   max_width: int, draw: ImageDraw.Draw) -> List[str]:
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str, y_center: int,
                             font: ImageFont.FreeTypeFont, color: Tuple,
                             shadow: bool = True, max_width: int = 900) -> int:
        lines = self._wrap_text(text, font, max_width, draw)
        bbox_single = draw.textbbox((0, 0), "Ag", font=font)
        line_h = (bbox_single[3] - bbox_single[1]) + 10
        total_h = line_h * len(lines)
        y = y_center - total_h // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            x = (VIDEO_WIDTH - w) // 2
            if shadow:
                draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 140))
            draw.text((x, y), line, font=font, fill=color)
            y += line_h
        return y

    def create_frame(self, title: str, content_lines: List[str],
                     theme: Dict, frame_num: int, total_frames: int,
                     hashtags: str = "", channel_name: str = "") -> Image.Image:
        img = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 255))
        draw = ImageDraw.Draw(img)

        self._draw_gradient_bg(draw, theme)
        self._draw_decorations(draw, theme)

        progress = frame_num / max(total_frames - 1, 1)

        title_font = self._get_font(72, bold=True)
        content_font = self._get_font(52)
        small_font = self._get_font(36)
        tag_font = self._get_font(38, bold=True)

        accent_bar_h = 120
        draw.rectangle([0, VIDEO_HEIGHT // 2 - accent_bar_h // 2,
                        VIDEO_WIDTH, VIDEO_HEIGHT // 2 + accent_bar_h // 2],
                       fill=theme["accent"] + (20,))

        title_y = 320
        self._draw_centered_text(draw, title, title_y, title_font, theme["text"], shadow=True)

        sep_y = 480
        sep_w = 200
        draw.rectangle(
            [(VIDEO_WIDTH - sep_w) // 2, sep_y - 3,
             (VIDEO_WIDTH + sep_w) // 2, sep_y + 3],
            fill=theme["accent"]
        )

        visible_lines = max(1, int(len(content_lines) * min(progress * 2, 1.0)))
        start_y = 560
        line_spacing = 90
        for i, line in enumerate(content_lines[:visible_lines]):
            y = start_y + i * line_spacing
            if y > VIDEO_HEIGHT - 300:
                break
            self._draw_centered_text(draw, line, y, content_font, theme["sub"], shadow=True)

        if hashtags:
            self._draw_centered_text(draw, hashtags, VIDEO_HEIGHT - 200,
                                     tag_font, theme["accent"], shadow=False, max_width=950)

        if channel_name:
            self._draw_centered_text(draw, f"@{channel_name}", VIDEO_HEIGHT - 120,
                                     small_font, theme["sub"], shadow=False)

        prog_w = int(VIDEO_WIDTH * progress)
        draw.rectangle([0, VIDEO_HEIGHT - 8, prog_w, VIDEO_HEIGHT], fill=theme["accent"])

        return img.convert("RGB")

    def create_video(self, video_data: Dict, custom_title: str = "",
                     custom_content: str = "", channel_name: str = "",
                     duration: int = 30, callback=None) -> str:
        try:
            from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips
            import moviepy.editor as mpe
        except ImportError:
            raise ImportError("moviepy yuklu degil. Lutfen 'pip install moviepy' calistirin.")

        title = custom_title or video_data.get("title", "Trending Video")
        tags = video_data.get("tags", [])[:5]
        hashtags = " ".join(f"#{t.replace(' ', '')}" for t in tags) if tags else "#shorts #viral #trending"

        if custom_content:
            content_lines = [line.strip() for line in custom_content.strip().split("\n") if line.strip()]
        else:
            desc = video_data.get("description", "")
            sentences = [s.strip() for s in desc.replace("\n", ". ").split(".") if len(s.strip()) > 20]
            content_lines = sentences[:6] if sentences else [
                "Bu video trend konulari iceriyor",
                "Izlemeye devam edin!",
                "Begeni ve abone olmay\u0131 unutmayin",
            ]

        theme = random.choice(COLOR_THEMES)
        total_frames = duration * FPS
        frames = []

        if callback:
            callback(0, total_frames, "Kareler olusturuluyor...")

        for i in range(total_frames):
            frame = self.create_frame(
                title=title,
                content_lines=content_lines,
                theme=theme,
                frame_num=i,
                total_frames=total_frames,
                hashtags=hashtags,
                channel_name=channel_name,
            )
            frames.append(np.array(frame))
            if callback and i % 30 == 0:
                callback(i, total_frames, f"Kare {i}/{total_frames} olusturuldu")

        if callback:
            callback(total_frames - 1, total_frames, "Video derleniyor...")

        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title[:40]).strip()
        output_path = str(self.output_dir / f"{safe_title}.mp4")

        clip = ImageSequenceClip(frames, fps=FPS)
        clip.write_videofile(
            output_path,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None,
            ffmpeg_params=["-crf", "23", "-preset", "fast"],
        )
        clip.close()

        if callback:
            callback(total_frames, total_frames, "Video tamamlandi!")

        return output_path

    def add_tts_audio(self, video_path: str, text: str, lang: str = "tr") -> str:
        try:
            from gtts import gTTS
            from moviepy.editor import VideoFileClip, AudioFileClip
        except ImportError:
            return video_path

        audio_path = video_path.replace(".mp4", "_audio.mp3")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(audio_path)

        out_path = video_path.replace(".mp4", "_final.mp4")
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)
        video = video.set_audio(audio.set_duration(video.duration))
        video.write_videofile(out_path, codec="libx264", audio_codec="aac",
                              verbose=False, logger=None)
        video.close()
        audio.close()

        try:
            os.remove(audio_path)
            os.remove(video_path)
        except Exception:
            pass

        return out_path
