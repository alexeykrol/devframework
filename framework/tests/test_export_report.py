import importlib.util
import json
import tempfile
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
export_report = load_module("export_report_module", EXPORT_PATH)


class ExportReportTests(unittest.TestCase):
    def test_parse_run_id_from_summary(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            summary = tmp / "orchestrator-run-summary.md"
            summary.write_text("- Run ID: RUN123\n", encoding="utf-8")
            old_summary = export_report.SUMMARY_PATH
            export_report.SUMMARY_PATH = summary
            try:
                self.assertEqual(export_report.parse_run_id(), "RUN123")
            finally:
                export_report.SUMMARY_PATH = old_summary

    def test_parse_run_id_from_jsonl(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            logs_dir = tmp / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            jsonl = logs_dir / "framework-run.jsonl"
            jsonl.write_text(
                "\n".join(
                    [
                        json.dumps({"event": "run_start", "run_id": "old"}),
                        json.dumps({"event": "run_end", "run_id": "newer"}),
                    ]
                ),
                encoding="utf-8",
            )
            old_summary = export_report.SUMMARY_PATH
            old_logs = export_report.LOGS_DIR
            export_report.SUMMARY_PATH = tmp / "missing-summary.md"
            export_report.LOGS_DIR = logs_dir
            try:
                self.assertEqual(export_report.parse_run_id(), "newer")
            finally:
                export_report.SUMMARY_PATH = old_summary
                export_report.LOGS_DIR = old_logs


if __name__ == "__main__":
    unittest.main()
