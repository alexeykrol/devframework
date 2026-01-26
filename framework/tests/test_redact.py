import importlib.util
import unittest
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]
EXPORT_PATH = ROOT / "framework" / "tools" / "export-report.py"
export_report = load_module("export_report", EXPORT_PATH)


class RedactionTests(unittest.TestCase):
    def test_redact_text_masks_common_secrets(self):
        sample = (
            "API_KEY=secret123\n"
            "authorization: Bearer abcdef\n"
            "aws_secret_access_key=XYZ\n"
            "token: tok_abc\n"
            "ghp_abcdefghijklmnopqrstuvwxyz123456\n"
            "sk_live_ABCdef1234567890\n"
        )
        redacted = export_report.redact_text(sample)
        self.assertNotIn("secret123", redacted)
        self.assertNotIn("abcdef", redacted)
        self.assertNotIn("XYZ", redacted)
        self.assertNotIn("tok_abc", redacted)
        self.assertNotIn("ghp_abcdefghijklmnopqrstuvwxyz123456", redacted)
        self.assertNotIn("sk_live_ABCdef1234567890", redacted)
        self.assertIn("***", redacted)


if __name__ == "__main__":
    unittest.main()
