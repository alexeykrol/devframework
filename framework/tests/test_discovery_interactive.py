import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "framework" / "tools" / "interactive-runner.py"
WATCHER = ROOT / "framework" / "tools" / "protocol-watch.py"


class InteractiveDiscoveryTests(unittest.TestCase):
    def test_interactive_runner_uses_tty_and_logs_prompt(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            prompt = tmp / "prompt.md"
            transcript = tmp / "transcript.log"
            prompt.write_text("HELLO\n", encoding="utf-8")

            child = (
                "import sys\n"
                "print('TTY=%d' % (1 if sys.stdin.isatty() else 0))\n"
                "line = sys.stdin.readline().strip()\n"
                "print('LINE=' + line)\n"
            )
            cmd = [
                sys.executable,
                str(RUNNER),
                "--transcript",
                str(transcript),
                "--prompt-file",
                str(prompt),
                "--",
                sys.executable,
                "-c",
                child,
            ]
            res = subprocess.run(cmd, check=False, text=True)
            self.assertEqual(res.returncode, 0)
            data = transcript.read_text(encoding="utf-8", errors="ignore")
            self.assertIn("TTY=1", data)
            self.assertIn("LINE=HELLO", data)

    def test_interactive_runner_prompt_arg_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            prompt = tmp / "prompt.md"
            transcript = tmp / "transcript.log"
            prompt.write_text("HELLO ARG", encoding="utf-8")

            child = (
                "import sys\n"
                "print('ARGC=%d' % len(sys.argv))\n"
                "print('ARG=' + sys.argv[1])\n"
            )
            cmd = [
                sys.executable,
                str(RUNNER),
                "--transcript",
                str(transcript),
                "--prompt-file",
                str(prompt),
                "--prompt-mode",
                "arg",
                "--",
                sys.executable,
                "-c",
                child,
            ]
            res = subprocess.run(cmd, check=False, text=True)
            self.assertEqual(res.returncode, 0)
            data = transcript.read_text(encoding="utf-8", errors="ignore")
            self.assertIn("ARGC=2", data)
            self.assertIn("ARG=HELLO ARG", data)

    def test_protocol_watch_tails_latest_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            logs = tmp / "logs"
            logs.mkdir(parents=True, exist_ok=True)
            events = logs / "framework-run.jsonl"
            log_file = logs / "task.log"
            log_file.write_text("start\n", encoding="utf-8")

            events.write_text(
                "\n".join(
                    [
                        "{\"event\": \"run_start\", \"run_id\": \"old\", \"phase\": \"legacy\"}",
                        "{\"event\": \"run_end\", \"run_id\": \"old\", \"phase\": \"legacy\"}",
                        "{\"event\": \"run_start\", \"run_id\": \"new\", \"phase\": \"discovery\"}",
                        (
                            "{\"event\": \"task_start\", \"run_id\": \"new\", "
                            "\"task\": \"discovery\", \"log\": \"" + str(log_file) + "\"}"
                        ),
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(2)"])
            watcher = subprocess.Popen(
                [
                    sys.executable,
                    str(WATCHER),
                    "--pid",
                    str(sleeper.pid),
                    "--logs-dir",
                    str(logs),
                    "--stall-timeout",
                    "0",
                    "--status-interval",
                    "0",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(0.5)
            self.assertIsNone(watcher.poll())
            watcher.terminate()
            sleeper.terminate()
            watcher.wait(timeout=2)
            sleeper.wait(timeout=2)


if __name__ == "__main__":
    unittest.main()
