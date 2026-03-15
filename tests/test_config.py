import sys
import os
import json
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DEFAULTS = {
    "ai_provider": "openai",
    "ai_api_key": "",
    "channel_name": "",
    "output_dir": "output_videos",
    "video_duration": 30,
}


def _import_main_funcs(config_path):
    import importlib
    import main as m
    return m


class TestLoadConfig(unittest.TestCase):
    def test_load_config_defaults_when_no_file(self):
        tmpdir = tempfile.mkdtemp()
        cfg_path = os.path.join(tmpdir, "config.json")
        with patch("main.CONFIG_FILE", cfg_path):
            import main
            cfg = main.load_config()
        for key, val in DEFAULTS.items():
            self.assertEqual(cfg[key], val)

    def test_load_config_reads_existing_file(self):
        tmpdir = tempfile.mkdtemp()
        cfg_path = os.path.join(tmpdir, "config.json")
        data = {**DEFAULTS, "api_key": "MY_KEY", "channel_name": "TestKanal"}
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        with patch("main.CONFIG_FILE", cfg_path):
            import main
            cfg = main.load_config()
        self.assertEqual(cfg["api_key"], "MY_KEY")
        self.assertEqual(cfg["channel_name"], "TestKanal")

    def test_load_config_corrupt_json_returns_defaults(self):
        tmpdir = tempfile.mkdtemp()
        cfg_path = os.path.join(tmpdir, "config.json")
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write("{not valid json!!!")
        with patch("main.CONFIG_FILE", cfg_path):
            import main
            cfg = main.load_config()
        for key, val in DEFAULTS.items():
            self.assertEqual(cfg[key], val)

    def test_load_config_missing_keys_get_defaults(self):
        tmpdir = tempfile.mkdtemp()
        cfg_path = os.path.join(tmpdir, "config.json")
        with open(cfg_path, "w", encoding="utf-8") as f:
            json.dump({"api_key": "ONLY_THIS"}, f)
        with patch("main.CONFIG_FILE", cfg_path):
            import main
            cfg = main.load_config()
        self.assertEqual(cfg["api_key"], "ONLY_THIS")


class TestSaveConfig(unittest.TestCase):
    def test_save_config_writes_json(self):
        tmpdir = tempfile.mkdtemp()
        cfg_path = os.path.join(tmpdir, "config.json")
        test_cfg = {**DEFAULTS, "api_key": "SAVED_KEY", "channel_name": "BotKanal"}
        with patch("main.CONFIG_FILE", cfg_path):
            import main
            main.save_config(test_cfg)
        with open(cfg_path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        self.assertEqual(loaded["api_key"], "SAVED_KEY")
        self.assertEqual(loaded["channel_name"], "BotKanal")

    def test_save_config_valid_json_structure(self):
        tmpdir = tempfile.mkdtemp()
        cfg_path = os.path.join(tmpdir, "config.json")
        with patch("main.CONFIG_FILE", cfg_path):
            import main
            main.save_config(DEFAULTS)
        with open(cfg_path, "r", encoding="utf-8") as f:
            content = f.read()
        parsed = json.loads(content)
        self.assertIsInstance(parsed, dict)


if __name__ == "__main__":
    unittest.main()
