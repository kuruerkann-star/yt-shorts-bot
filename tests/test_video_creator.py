import sys
import os
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from video_creator import VideoCreator, VIDEO_WIDTH, VIDEO_HEIGHT, COLOR_THEMES
from PIL import Image, ImageDraw, ImageFont


class TestFindFonts(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.creator = VideoCreator(output_dir=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_find_fonts_returns_dict(self):
        fonts = self.creator._find_fonts()
        self.assertIn("bold", fonts)
        self.assertIn("regular", fonts)

    def test_find_fonts_values_are_none_or_str(self):
        fonts = self.creator._find_fonts()
        for key, val in fonts.items():
            self.assertTrue(val is None or isinstance(val, str))

    def test_get_font_returns_font_object(self):
        font = self.creator._get_font(48)
        self.assertIsInstance(font, ImageFont.FreeTypeFont)

    def test_get_font_bold(self):
        font = self.creator._get_font(48, bold=True)
        self.assertIsNotNone(font)


class TestWrapText(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.creator = VideoCreator(output_dir=self.tmpdir)
        img = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT))
        self.draw = ImageDraw.Draw(img)
        self.font = self.creator._get_font(52)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_wrap_text_single_short_line(self):
        lines = self.creator._wrap_text("Kisa metin", self.font, 900, self.draw)
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "Kisa metin")

    def test_wrap_text_long_text_splits(self):
        long_text = "Bu cok uzun bir metin satiridir ve mutlaka birden fazla satira bolunmesi gerekir cunku genisligi asiyor"
        lines = self.creator._wrap_text(long_text, self.font, 700, self.draw)
        self.assertGreater(len(lines), 1)

    def test_wrap_text_empty_string(self):
        lines = self.creator._wrap_text("", self.font, 900, self.draw)
        self.assertEqual(lines, [])

    def test_wrap_text_no_line_exceeds_max_width(self):
        long_text = "Bu uzun bir cumle olup kelimeler aralanarak bolunmeli maksimum genislige gore ayarlanmali"
        max_w = 600
        lines = self.creator._wrap_text(long_text, self.font, max_w, self.draw)
        for line in lines:
            bbox = self.draw.textbbox((0, 0), line, font=self.font)
            w = bbox[2] - bbox[0]
            self.assertLessEqual(w, max_w)


class TestCreateFrame(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.creator = VideoCreator(output_dir=self.tmpdir)
        self.theme = COLOR_THEMES[0]
        self.content_lines = ["Satir 1", "Satir 2", "Satir 3", "Satir 4"]

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_create_frame_returns_rgb_image(self):
        img = self.creator.create_frame(
            title="Test Baslik",
            content_lines=self.content_lines,
            theme=self.theme,
            frame_num=0,
            total_frames=30,
        )
        self.assertIsInstance(img, Image.Image)
        self.assertEqual(img.mode, "RGB")
        self.assertEqual(img.size, (VIDEO_WIDTH, VIDEO_HEIGHT))

    def test_create_frame_progress_zero(self):
        total = 900
        img = self.creator.create_frame(
            title="Test",
            content_lines=self.content_lines,
            theme=self.theme,
            frame_num=0,
            total_frames=total,
        )
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (VIDEO_WIDTH, VIDEO_HEIGHT))

    def test_create_frame_progress_full(self):
        total = 900
        img = self.creator.create_frame(
            title="Test",
            content_lines=self.content_lines,
            theme=self.theme,
            frame_num=total - 1,
            total_frames=total,
        )
        self.assertIsNotNone(img)
        self.assertEqual(img.size, (VIDEO_WIDTH, VIDEO_HEIGHT))

    def test_create_frame_with_hashtags_and_channel(self):
        img = self.creator.create_frame(
            title="Hashtag Testi",
            content_lines=["Icerik"],
            theme=self.theme,
            frame_num=15,
            total_frames=30,
            hashtags="#shorts #viral",
            channel_name="TestKanal",
        )
        self.assertEqual(img.mode, "RGB")

    def test_create_frame_all_themes(self):
        for theme in COLOR_THEMES:
            img = self.creator.create_frame(
                title="Tema Testi",
                content_lines=["line"],
                theme=theme,
                frame_num=0,
                total_frames=30,
            )
            self.assertEqual(img.size, (VIDEO_WIDTH, VIDEO_HEIGHT))


class TestOutputDir(unittest.TestCase):
    def test_output_dir_created(self):
        tmpdir = tempfile.mkdtemp()
        target = os.path.join(tmpdir, "subdir", "videos")
        creator = VideoCreator(output_dir=target)
        self.assertTrue(os.path.isdir(target))
        shutil.rmtree(tmpdir, ignore_errors=True)


class TestCreateVideoNoMoviepy(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.creator = VideoCreator(output_dir=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_create_video_no_moviepy_raises(self):
        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def fake_import(name, *args, **kwargs):
            if name == "moviepy":
                raise ImportError("moviepy yuklu degil")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=fake_import):
            with self.assertRaises(ImportError):
                self.creator.create_video(
                    video_data={"title": "Test"},
                    custom_title="Test",
                    duration=1,
                )


if __name__ == "__main__":
    unittest.main()
