#!/usr/bin/env python3
import argparse
import os
import select
import signal
import subprocess
import sys
import time
from pathlib import Path


def iso_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


def run_interactive(
    command: list[str],
    transcript: Path,
    pause_marker: Path | None,
    pause_cmd: str,
    prompt_file: Path | None,
    append: bool,
) -> int:
    transcript.parent.mkdir(parents=True, exist_ok=True)
    log_f = transcript.open("ab" if append else "wb")

    master_fd, slave_fd = os.openpty()
    if len(command) == 1:
        proc = subprocess.Popen(
            command[0],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            shell=True,
            preexec_fn=os.setsid,
        )
    else:
        proc = subprocess.Popen(
            command,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            shell=False,
            preexec_fn=os.setsid,
        )
    os.close(slave_fd)

    stdin_fd = sys.stdin.fileno()
    stdout_fd = sys.stdout.fileno()
    buffer = b""
    pause_requested = False
    pause_deadline = None

    def send_prompt() -> None:
        if not prompt_file:
            return
        try:
            text = prompt_file.read_text(encoding="utf-8")
        except Exception:
            return
        payload = text.rstrip() + "\n"
        os.write(master_fd, payload.encode("utf-8"))

    # Send initial prompt once to seed the interactive session.
    send_prompt()

    def write_pause_marker() -> None:
        if not pause_marker:
            return
        pause_marker.parent.mkdir(parents=True, exist_ok=True)
        pause_marker.write_text(
            f"paused_at: {iso_ts()}\ncommand: {pause_cmd}\n", encoding="utf-8"
        )

    try:
        while True:
            if proc.poll() is not None:
                break
            read_fds = [master_fd, stdin_fd]
            ready, _, _ = select.select(read_fds, [], [], 0.25)
            if master_fd in ready:
                data = os.read(master_fd, 4096)
                if not data:
                    break
                os.write(stdout_fd, data)
                log_f.write(data)
                log_f.flush()
            if stdin_fd in ready:
                data = os.read(stdin_fd, 4096)
                if not data:
                    break
                # Forward user input immediately to child.
                os.write(master_fd, data)
                buffer += data
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        decoded = line.decode("utf-8", errors="ignore").strip()
                    except Exception:
                        decoded = ""
                    if decoded == pause_cmd and not pause_requested:
                        pause_requested = True
                        pause_deadline = time.time() + 20
                        message = (
                            f"\n[PAUSE] Session paused at {iso_ts()}. "
                            "Re-run ./install-framework.sh to resume.\n"
                        )
                        os.write(stdout_fd, message.encode("utf-8"))
                        log_f.write(message.encode("utf-8"))
                        log_f.flush()
                        write_pause_marker()
            if pause_requested and pause_deadline and time.time() >= pause_deadline:
                try:
                    proc.send_signal(signal.SIGTERM)
                except Exception:
                    pass
                time.sleep(1)
                if proc.poll() is None:
                    try:
                        proc.send_signal(signal.SIGKILL)
                    except Exception:
                        pass
                return 2
    finally:
        try:
            os.close(master_fd)
        except Exception:
            pass
        log_f.close()

    if pause_requested:
        return 2
    return proc.wait()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run interactive command with transcript logging.")
    parser.add_argument("--transcript", required=True)
    parser.add_argument("--pause-marker")
    parser.add_argument("--pause-command", default="/pause")
    parser.add_argument("--prompt-file")
    parser.add_argument("--append", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    cmd = list(args.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        raise SystemExit("Missing command to run. Use: interactive-runner.py -- <command>")

    transcript = Path(args.transcript).resolve()
    pause_marker = Path(args.pause_marker).resolve() if args.pause_marker else None
    prompt_file = Path(args.prompt_file).resolve() if args.prompt_file else None
    return run_interactive(
        cmd,
        transcript,
        pause_marker,
        args.pause_command,
        prompt_file,
        args.append,
    )


if __name__ == "__main__":
    raise SystemExit(main())
