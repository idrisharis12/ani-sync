"""Unit tests for ani-sync core functions using Python's standard unittest."""

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import ani_sync
from ani_sync import config


class TestSanitization(unittest.TestCase):
    def test_sanitize_filename_standard(self):
        title = "Attack on Titan: The Final Season / Part 2? *cool*"
        sanitized = ani_sync.sanitize_filename(title)
        self.assertNotIn(":", sanitized)
        self.assertNotIn("/", sanitized)
        self.assertNotIn("?", sanitized)
        self.assertNotIn("*", sanitized)
        self.assertIn("Attack on Titan", sanitized)

    def test_sanitize_filename_clean(self):
        title = "Frieren_EP01"
        self.assertEqual(ani_sync.sanitize_filename(title), "Frieren_EP01")


class TestThemeEngine(unittest.TestCase):
    def test_apply_valid_theme(self):
        self.assertTrue(ani_sync.apply_theme("tokyonight"))
        self.assertEqual(ani_sync.CURRENT_THEME, "tokyonight")

    def test_apply_catppuccin_theme(self):
        self.assertTrue(ani_sync.apply_theme("catppuccin"))
        self.assertEqual(ani_sync.CURRENT_THEME, "catppuccin")

    def test_apply_invalid_theme(self):
        self.assertFalse(ani_sync.apply_theme("non_existent_theme"))


class TestConfigHandling(unittest.TestCase):
    def test_secure_config_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            cfg_file = tmp_path / "config.env"

            orig_dir = config.CONFIG_DIR
            orig_path = config.CONFIG_PATH
            try:
                config.CONFIG_DIR = tmp_path
                config.CONFIG_PATH = cfg_file

                config._append_config("TEST_KEY", "secret_value_123")

                self.assertTrue(cfg_file.exists())
                content = cfg_file.read_text(encoding="utf-8")
                self.assertIn('export TEST_KEY="secret_value_123"', content)

                if not config.IS_WINDOWS:
                    mode = oct(cfg_file.stat().st_mode & 0o777)
                    self.assertEqual(mode, "0o600")
            finally:
                config.CONFIG_DIR = orig_dir
                config.CONFIG_PATH = orig_path


class TestHistory(unittest.TestCase):
    def test_save_and_load_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            hist_file = Path(tmpdir) / "history.json"
            orig_dir = config.CONFIG_DIR
            orig_path = config.HISTORY_PATH
            try:
                config.CONFIG_DIR = Path(tmpdir)
                config.HISTORY_PATH = hist_file

                config.save_history("frieren-1234", "Frieren", 5, quality="1080p", mode="sub")

                data = config.load_history()
                self.assertIn("history", data)
                self.assertEqual(len(data["history"]), 1)
                self.assertEqual(data["history"][0]["slug"], "frieren-1234")
                self.assertEqual(data["history"][0]["title"], "Frieren")
                self.assertEqual(data["history"][0]["episode"], 5)

                last = config.get_last_watched()
                self.assertIsNotNone(last)
                self.assertEqual(last["title"], "Frieren")
                self.assertEqual(last["episode"], 5)
            finally:
                config.CONFIG_DIR = orig_dir
                config.HISTORY_PATH = orig_path


class TestQualitySorting(unittest.TestCase):
    def test_sort_qualities(self):
        qualities = ["360p", "1080p", "720p", "480p"]

        def sort_key(q):
            num = re.findall(r"\d+", q)
            return int(num[0]) if num else 0

        sorted_q = sorted(qualities, key=sort_key, reverse=True)
        self.assertEqual(sorted_q, ["1080p", "720p", "480p", "360p"])


class TestMultiProvider(unittest.TestCase):
    def test_provider_registry(self):
        from ani_sync.providers.manager import PROVIDERS
        self.assertIn("anidb", PROVIDERS)
        self.assertIn("gogo", PROVIDERS)
        self.assertIn("hianime", PROVIDERS)


if __name__ == "__main__":
    unittest.main()
