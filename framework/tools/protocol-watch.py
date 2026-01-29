#!/usr/bin/env python3
import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path


def iso_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def format_duration(seconds: float) -> str:
    total = int(seconds)
    minutes, sec = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def write_alert(log_path: Path, message: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{iso_ts()} {message}\n")


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    else:
        return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch a framework run and report progress/stalls.")
    parser.add_argument("--pid", type=int, required=True, help="Orchestrator PID to watch")
    parser.add_argument("--logs-dir", default="framework/logs")
    parser.add_argument("--stall-timeout", type=int, default=900)
    parser.add_argument("--poll-interval", type=float, default=2.0)
    parser.add_argument("--status-interval", type=int, default=10)
    parser.add_argument("--kill-on-stall", action="store_true")
    args = parser.parse_args()

    logs_dir = Path(args.logs_dir)
    events_path = logs_dir / "framework-run.jsonl"
    alerts_path = logs_dir / "protocol-alerts.log"
    status_path = logs_dir / "protocol-status.log"

    last_pos = 0
    active_task = None
    active_log = None
    last_log_mtime = None
    last_log_check = time.time()
    run_id = None
    phase = None
    run_started_at = None
    tasks_total = None
    status = {}
    active_interactive = False
    status_interval = args.status_interval
    if status_interval <= 0:
        status_interval = None
    next_status_at = time.time() + status_interval if status_interval else None

    print("[WATCH] protocol monitor started")

    while True:
        if not pid_alive(args.pid):
            print("[WATCH] orchestrator exited")
            return

        if events_path.exists():
            with events_path.open("r", encoding="utf-8", errors="ignore") as f:
                f.seek(last_pos)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    event = payload.get("event")
                    if event == "run_start":
                        run_id = payload.get("run_id")
                        phase = payload.get("phase")
                        run_started_at = time.time()
                        tasks_total = payload.get("tasks_total")
                        status = {}
                    elif event == "task_start":
                        active_task = payload.get("task")
                        active_log = payload.get("log")
                        active_interactive = bool(payload.get("interactive"))
                        last_log_mtime = None
                        if active_task:
                            status[active_task] = "RUNNING"
                        print(f"[TASK] start {active_task}")
                    elif event == "task_end":
                        name = payload.get("task")
                        code = payload.get("exit_code")
                        print(f"[TASK] done {name} exit={code}")
                        if name:
                            status[name] = "OK" if code == 0 else f"FAIL({code})"
                        if name == active_task:
                            active_task = None
                            active_log = None
                            last_log_mtime = None
                            active_interactive = False
                    elif event == "run_end":
                        print("[WATCH] run_end")
                        return
                last_pos = f.tell()

        # stall detection
        now = time.time()
        if status_interval and now >= next_status_at and phase:
            running = [k for k, v in status.items() if v == "RUNNING"]
            done = [k for k, v in status.items() if v.startswith("OK") or v.startswith("FAIL")]
            total = tasks_total if tasks_total is not None else len(status)
            elapsed = format_duration(now - run_started_at) if run_started_at else "00:00"
            running_str = ",".join(running) if running else "-"
            line = (
                f"[STATUS] phase={phase} run_id={run_id} "
                f"running={running_str} done={len(done)}/{total} elapsed={elapsed}"
            )
            status_path.parent.mkdir(parents=True, exist_ok=True)
            with status_path.open("a", encoding="utf-8") as f:
                f.write(f"{iso_ts()} {line}\n")
            if not (active_interactive and phase == "discovery"):
                print(line)
            next_status_at = now + status_interval

        if active_log and args.stall_timeout > 0 and now - last_log_check >= args.poll_interval:
            log_path = Path(active_log)
            if log_path.exists():
                mtime = log_path.stat().st_mtime
                if last_log_mtime is None:
                    last_log_mtime = mtime
                else:
                    if mtime == last_log_mtime:
                        stalled_for = int(now - mtime)
                        if stalled_for >= args.stall_timeout:
                            message = (
                                f"[ALERT] task '{active_task}' stalled for {stalled_for}s "
                                f"(log: {log_path})"
                            )
                            print(message)
                            write_alert(alerts_path, message)
                            if args.kill_on_stall and not (active_interactive and phase == "discovery"):
                                try:
                                    os.kill(args.pid, signal.SIGTERM)
                                except Exception:
                                    pass
                                time.sleep(2)
                                if pid_alive(args.pid):
                                    try:
                                        os.kill(args.pid, signal.SIGKILL)
                                    except Exception:
                                        pass
                            return
                    else:
                        last_log_mtime = mtime
            last_log_check = now

        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
