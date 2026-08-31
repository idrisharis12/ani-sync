"""Unit tests for ani-sync core functions using Python's standard unittest."""

import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import ani_sync


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

            orig_dir = ani_sync.CONFIG_DIR
            orig_path = ani_sync.CONFIG_PATH
            try:
                ani_sync.CONFIG_DIR = tmp_path
                ani_sync.CONFIG_PATH = cfg_file

                ani_sync._append_config("TEST_KEY", "secret_value_123")

                self.assertTrue(cfg_file.exists())
                content = cfg_file.read_text(encoding="utf-8")
                self.assertIn('export TEST_KEY="secret_value_123"', content)

                if not ani_sync.IS_WINDOWS:
                    mode = oct(cfg_file.stat().st_mode & 0o777)
                    self.assertEqual(mode, "0o600")
            finally:
                ani_sync.CONFIG_DIR = orig_dir
                ani_sync.CONFIG_PATH = orig_path


class TestHistory(unittest.TestCase):
    def test_save_and_load_history(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            hist_file = Path(tmpdir) / "history.json"
            orig_dir = ani_sync.CONFIG_DIR
            orig_path = ani_sync.HISTORY_PATH
            try:
                ani_sync.CONFIG_DIR = Path(tmpdir)
                ani_sync.HISTORY_PATH = hist_file

                ani_sync.save_history("frieren-1234", "Frieren", 5, quality="1080p", mode="sub")

                data = ani_sync.load_history()
                self.assertIn("history", data)
                self.assertEqual(len(data["history"]), 1)
                self.assertEqual(data["history"][0]["slug"], "frieren-1234")
                self.assertEqual(data["history"][0]["title"], "Frieren")
                self.assertEqual(data["history"][0]["episode"], 5)

                last = ani_sync.get_last_watched()
                self.assertIsNotNone(last)
                self.assertEqual(last["title"], "Frieren")
                self.assertEqual(last["episode"], 5)
            finally:
                ani_sync.CONFIG_DIR = orig_dir
                ani_sync.HISTORY_PATH = orig_path


class TestQualitySorting(unittest.TestCase):
    def test_sort_qualities(self):
        qualities = ["360p", "1080p", "720p", "480p"]

        def sort_key(q):
            num = re.findall(r"\d+", q)
            return int(num[0]) if num else 0

        sorted_q = sorted(qualities, key=sort_key, reverse=True)
        self.assertEqual(sorted_q, ["1080p", "720p", "480p", "360p"])


if __name__ == "__main__":
    unittest.main()
