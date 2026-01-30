#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORCH = ROOT / "orchestrator" / "orchestrator.py"
WATCH = ROOT / "tools" / "protocol-watch.py"


def truthy(value: str | None) -> bool:
    if not value:
        return False
    return value.strip().lower() in ("1", "true", "yes", "on")


def latest_summary(phase: str) -> Path | None:
    docs_dir = ROOT / "docs"
    if not docs_dir.exists():
        return None
    candidates = sorted(docs_dir.glob(f"orchestrator-run-summary-{phase}-*.md"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def summary_success(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "- Error:" in text:
        return False
    if "PAUSED" in text:
        return False
    for line in text.splitlines():
        if line.strip().endswith(": FAIL") or "FAIL (" in line or "BLOCKED" in line:
            return False
    return True


def phase_completed(phase: str) -> bool:
    summary = latest_summary(phase)
    if not summary:
        return False
    return summary_success(summary)


def run_phase(config: Path, phase: str, logs_dir: Path) -> int:
    cmd = [sys.executable, str(ORCH), "--config", str(config), "--phase", phase]
    env = os.environ.copy()
    proc = subprocess.Popen(cmd, env=env)
    pid_path = logs_dir / "orchestrator.pid"
    logs_dir.mkdir(parents=True, exist_ok=True)
    pid_path.write_text(str(proc.pid), encoding="utf-8")

    watch_cmd = [
        sys.executable,
        str(WATCH),
        "--pid",
        str(proc.pid),
        "--logs-dir",
        str(logs_dir),
        "--stall-timeout",
        str(int(os.getenv("FRAMEWORK_STALL_TIMEOUT", "900"))),
        "--poll-interval",
        str(float(os.getenv("FRAMEWORK_WATCH_POLL", "2"))),
        "--status-interval",
        str(int(os.getenv("FRAMEWORK_STATUS_INTERVAL", "10"))),
    ]
    if os.getenv("FRAMEWORK_STALL_KILL", "1").strip().lower() in ("1", "true", "yes", "on"):
        watch_cmd.append("--kill-on-stall")
    watcher = subprocess.Popen(watch_cmd)

    code = proc.wait()
    watcher.wait(timeout=5)
    try:
        pid_path.unlink()
    except FileNotFoundError:
        pass
    return code


def determine_mode(default_phase: str | None) -> list[str]:
    if default_phase:
        return [default_phase]
    # auto-detect empty host vs legacy
    root = Path.cwd()
    ignore = {
        "framework",
        "framework.zip",
        "install-framework.sh",
        "AGENTS.md",
        "AGENTS.override.md",
        ".git",
        ".gitignore",
        ".DS_Store",
    }
    for entry in root.iterdir():
        if entry.name in ignore:
            continue
        phases = ["legacy", "discovery"]
        if truthy(os.getenv("FRAMEWORK_SKIP_DISCOVERY")):
            phases = ["legacy"]
        return phases
    return ["discovery"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run framework protocol with monitoring and resume.")
    parser.add_argument("--config", default=str(ROOT / "orchestrator" / "orchestrator.json"))
    parser.add_argument("--phase", choices=["legacy", "discovery", "main", "post"], help="Force single phase")
    args = parser.parse_args()

    config = Path(args.config).resolve()
    logs_dir = Path("framework/logs").resolve()

    phases = determine_mode(args.phase)
    resume = os.getenv("FRAMEWORK_RESUME", "1").strip().lower() in ("1", "true", "yes", "on")

    discovery_ok = False
    for phase in phases:
        if resume and phase_completed(phase):
            print(f"[RESUME] skip {phase} (already completed)")
            continue
        print(f"[PHASE] starting {phase}")
        code = run_phase(config, phase, logs_dir)
        if code == 2 and phase == "discovery":
            print("[PAUSED] discovery interview paused. Re-run ./install-framework.sh to continue.")
            return 0
        if code != 0:
            print(f"[ALERT] phase '{phase}' failed (exit={code})")
            return code
        if phase == "discovery":
            discovery_ok = True
        time.sleep(1)

    if discovery_ok:
        print("Discovery complete. Review the generated spec, then confirm start of development:")
        print("  python3 framework/orchestrator/orchestrator.py --phase main")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
