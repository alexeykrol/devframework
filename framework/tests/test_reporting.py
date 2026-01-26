import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ORCH_PATH = ROOT / "framework" / "orchestrator" / "orchestrator.py"


def load_module(name: str, path: Path):
    import importlib.util

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


orchestrator = load_module("orchestrator_reporting", ORCH_PATH)


class ReportingTests(unittest.TestCase):
    def test_dry_run_flag_added(self):
        cfg = {"reporting": {"enabled": True, "repo": "owner/name", "dry_run": True}}
        captured = {}

        def fake_run(cmd, check=False, text=True, capture_output=True):
            captured["cmd"] = cmd
            class Result:
                returncode = 0
                stdout = ""
                stderr = ""
            return Result()

        old_run = orchestrator.subprocess.run
        os.environ.pop("FRAMEWORK_REPORTING_DRY_RUN", None)
        try:
            orchestrator.subprocess.run = fake_run
            err = orchestrator.maybe_publish_report(
                cfg, "main", "RUN123", ROOT / "framework", "v1"
            )
            self.assertIsNone(err)
            self.assertIn("--dry-run", captured["cmd"])
        finally:
            orchestrator.subprocess.run = old_run


if __name__ == "__main__":
    unittest.main()
