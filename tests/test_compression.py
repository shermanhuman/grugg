import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "skills/grugg-compress"
sys.path.insert(0, str(SKILL))
from scripts.compress import compress_file, backup_for
from scripts.validate import validate
from scripts.detect import should_compress


class CompressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / "notes.md"
        self.original = b"# Rules\r\n\r\nAlways preserve every important condition.\r\n"
        self.source.write_bytes(self.original)
        self.source.chmod(0o640)
        self.candidate = self.root / "candidate.md"
        self.candidate.write_text("# Rules\n\nPreserve every important condition.\n")

    def test_candidate_replaces_after_validation_and_preserves_backup_bytes_and_mode(self):
        with patch("scripts.compress.call_claude") as call:
            self.assertTrue(compress_file(self.source, candidate=self.candidate))
            call.assert_not_called()
        self.assertEqual(backup_for(self.source).read_bytes(), self.original)
        self.assertEqual(self.source.read_bytes(), self.candidate.read_bytes())
        self.assertEqual(self.source.stat().st_mode & 0o777, 0o640)

    def test_credentials_do_not_implicitly_select_provider(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-only"}), patch("scripts.compress.call_claude") as call:
            with self.assertRaises(ValueError):
                compress_file(self.source)
            call.assert_not_called()
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_provider_failure_during_repair_leaves_original_and_no_backup(self):
        with patch("scripts.compress.call_claude", side_effect=["# Wrong heading\n", RuntimeError("offline")]):
            with self.assertRaises(RuntimeError):
                compress_file(self.source, provider="claude")
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertFalse(backup_for(self.source).exists())

    def test_initial_attempt_plus_two_repairs(self):
        with patch("scripts.compress.call_claude", side_effect=["# Wrong\n", "# Wrong again\n", self.candidate.read_text()]) as call:
            self.assertTrue(compress_file(self.source, provider="claude"))
            self.assertEqual(call.call_count, 3)

    def test_failed_validation_never_writes_source(self):
        self.candidate.write_text("# Changed heading\n")
        self.assertFalse(compress_file(self.source, candidate=self.candidate))
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertFalse(backup_for(self.source).exists())

    def test_existing_backup_is_preserved(self):
        backup_for(self.source).write_text("earlier backup")
        with self.assertRaises(FileExistsError):
            compress_file(self.source, candidate=self.candidate)
        self.assertEqual(backup_for(self.source).read_text(), "earlier backup")
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_concurrent_edit_wins(self):
        def provider(_):
            self.source.write_text("A newer user edit")
            return self.candidate.read_text()
        with patch("scripts.compress.call_claude", side_effect=provider):
            with self.assertRaises(RuntimeError):
                compress_file(self.source, provider="claude")
        self.assertEqual(self.source.read_text(), "A newer user edit")
        self.assertFalse(backup_for(self.source).exists())

    def test_symlink_is_rejected(self):
        link = self.root / "link.md"
        link.symlink_to(self.source)
        with self.assertRaises(ValueError):
            compress_file(link, candidate=self.candidate)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_invalid_utf8_is_not_silently_discarded(self):
        self.source.write_bytes(b"# Rules\n\xff")
        with self.assertRaises(UnicodeDecodeError):
            compress_file(self.source, candidate=self.candidate)
        self.assertEqual(self.source.read_bytes(), b"# Rules\n\xff")

    def test_protected_markdown_regions(self):
        pairs = [
            ("# Keep\n", "# Changed\n"),
            ("Use `a` here", "Use `b` here"),
            ("---\nname: one\n---\nBody", "---\nname: two\n---\nBody"),
            ("```sh\necho keep\n", "```sh\necho changed\n"),
            ("    echo keep\n", "    echo changed\n"),
            ("Read ./path/a", "Read ./path/b"),
            ("Retry at most 2 times", "Retry at most 3 times"),
            ("- Parent\n  - Child\n", "- Parent\n- Child\n"),
            ("| one | two |\n", "| one |\n"),
            ("[help](guide.md)", "[help](other.md)"),
        ]
        for original, changed in pairs:
            with self.subTest(original=original):
                self.source.write_text(original)
                self.candidate.write_text(changed)
                self.assertFalse(validate(self.source, self.candidate).is_valid)

    def test_dotenv_is_not_natural_language(self):
        env = self.root / ".env"
        env.write_text("API_KEY=placeholder\n")
        self.assertFalse(should_compress(env))

    def test_cli_requires_explicit_input_mode(self):
        result = subprocess.run([sys.executable, "-m", "scripts", str(self.source)], cwd=SKILL, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(self.source.read_bytes(), self.original)


if __name__ == "__main__":
    unittest.main()
