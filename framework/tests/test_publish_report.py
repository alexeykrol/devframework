import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PUBLISH = ROOT / "framework" / "tools" / "publish-report.py"


class PublishReportTests(unittest.TestCase):
    def test_dry_run_without_token(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            zip_path = tmp / "report.zip"
            zip_path.write_bytes(b"fake")
            res = subprocess.run(
                [
                    "python3",
                    str(PUBLISH),
                    "--repo",
                    "owner/name",
                    "--run-id",
                    "RUN123",
                    "--zip",
                    str(zip_path),
                    "--host-id",
                    "host",
                    "--dry-run",
                ],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(res.returncode, 0)
            self.assertIn("DRY-RUN: publish-report", res.stdout)


if __name__ == "__main__":
    unittest.main()
