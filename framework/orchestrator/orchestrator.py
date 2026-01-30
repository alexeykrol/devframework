#!/usr/bin/env python3
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, shell=True, check=False)


def resolve_path(value, base: Path) -> Path:
    path = value if isinstance(value, Path) else Path(value)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def write_pause_marker(path: Path, reason: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"paused_at: {iso_ts(time.time())}\nreason: {reason}\n", encoding="utf-8")


def is_git_repo(path: Path) -> bool:
    res = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--git-dir"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return res.returncode == 0


def is_git_worktree(path: Path) -> bool:
    res = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return res.returncode == 0


def get_git_common_dir(path: Path) -> Optional[Path]:
    res = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--git-common-dir"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
        text=True,
    )
    if res.returncode != 0:
        return None
    value = res.stdout.strip()
    if not value:
        return None
    common_dir = Path(value)
    if not common_dir.is_absolute():
        common_dir = (path / common_dir).resolve()
    else:
        common_dir = common_dir.resolve()
    return common_dir


def is_same_git_repo(project_root: Path, worktree_path: Path) -> bool:
    project_common = get_git_common_dir(project_root)
    worktree_common = get_git_common_dir(worktree_path)
    if project_common is None or worktree_common is None:
        return False
    return project_common == worktree_common


def get_git_commit(project_root: Path) -> str:
    res = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
        text=True,
    )
    if res.returncode == 0:
        return res.stdout.strip()
    return "unknown"


def branch_exists(project_root: Path, branch: str) -> bool:
    res = subprocess.run(
        ["git", "-C", str(project_root), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return res.returncode == 0


def get_framework_version(project_root: Path) -> str:
    version_file = project_root / "framework" / "VERSION"
    if version_file.exists():
        content = version_file.read_text(encoding="utf-8", errors="ignore").strip()
        if content:
            return content
    return get_git_commit(project_root)


def write_event(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")


def iso_ts(epoch: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(epoch))


def format_duration(seconds: float) -> str:
    total = int(seconds)
    minutes, sec = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:02d}:{sec:02d}"


def format_template(value, **kwargs):
    if value is None:
        return None
    if isinstance(value, Path):
        value = str(value)
    if not isinstance(value, str):
        return value
    try:
        return value.format(**kwargs)
    except KeyError as exc:
        raise RuntimeError(f"Unknown template key {exc} in value: {value}") from exc


def ensure_worktree(project_root: Path, worktree_path: Path, branch: str):
    if worktree_path.exists():
        if not is_git_worktree(worktree_path):
            raise RuntimeError(
                f"Worktree path exists but is not a git worktree: {worktree_path}"
            )
        if not is_same_git_repo(project_root, worktree_path):
            raise RuntimeError(
                "Worktree path exists but belongs to a different git repository: "
                f"{worktree_path}"
            )
        return
    if branch_exists(project_root, branch):
        cmd = f"git worktree add {worktree_path} {branch}"
        res = run(cmd, cwd=project_root)
        if res.returncode != 0:
            raise RuntimeError(
                "Failed to create worktree from existing branch. "
                f"Branch '{branch}' may already be checked out elsewhere."
            )
        return

    cmd = f"git worktree add -b {branch} {worktree_path}"
    res = run(cmd, cwd=project_root)
    if res.returncode != 0:
        cmd = f"git worktree add {worktree_path} {branch}"
        res = run(cmd, cwd=project_root)
    if res.returncode != 0:
        raise RuntimeError(f"Failed to create worktree: {worktree_path}")


def load_config(path: Path):
    suffix = path.suffix.lower()
    if suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            return json.load(f) or {}
    if suffix in (".yml", ".yaml"):
        if yaml is None:
            fallback = path.with_suffix(".json")
            if fallback.exists():
                return load_config(fallback)
            raise RuntimeError(
                "PyYAML is required to read YAML config. "
                f"Install PyYAML or use JSON config: {fallback}"
            )
        with path.open("r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        return cfg or {}
    # Unknown suffix: try JSON then YAML
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f) or {}
        except json.JSONDecodeError:
            pass
    if yaml is None:
        raise RuntimeError(f"Unsupported config format: {path}")
    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg or {}


def normalize_tasks(tasks):
    if not isinstance(tasks, list):
        raise RuntimeError("Config 'tasks' must be a list")
    tasks_by_name = {}
    ordered = []
    for task in tasks:
        if not isinstance(task, dict):
            raise RuntimeError("Each task must be a mapping")
        name = task.get("name")
        if not name:
            raise RuntimeError("Each task must have a non-empty 'name'")
        if name in tasks_by_name:
            raise RuntimeError(f"Duplicate task name: {name}")
        for required in ("worktree", "prompt"):
            if required not in task:
                raise RuntimeError(f"Task '{name}' missing required field '{required}'")
        task.setdefault("depends_on", [])
        if not isinstance(task["depends_on"], list):
            raise RuntimeError(f"Task '{name}': 'depends_on' must be a list")
        phase = task.get("phase", "main")
        if phase not in ("discovery", "main", "post", "legacy"):
            raise RuntimeError(f"Task '{name}': invalid phase '{phase}'")
        task["phase"] = phase
        manual = task.get("manual", False)
        if not isinstance(manual, bool):
            raise RuntimeError(f"Task '{name}': 'manual' must be boolean")
        task["manual"] = manual
        tasks_by_name[name] = task
        ordered.append(task)
    for name, task in tasks_by_name.items():
        for dep in task["depends_on"]:
            if dep not in tasks_by_name:
                raise RuntimeError(f"Task '{name}' depends on unknown task '{dep}'")
    return ordered, tasks_by_name


def select_tasks(tasks, phase: str, include_manual: bool):
    selected = []
    selected_names = set()
    for task in tasks:
        if task.get("phase", "main") != phase:
            continue
        if task.get("manual", False) and not include_manual:
            continue
        selected.append(task)
        selected_names.add(task["name"])
    for task in selected:
        missing = [dep for dep in task["depends_on"] if dep not in selected_names]
        if missing:
            raise RuntimeError(
                f"Task '{task['name']}' depends on excluded tasks: {', '.join(missing)}"
            )
    return selected


def build_command(runners, task, prompt_path: Path):
    runner_name = task.get("runner", "codex")
    if runner_name not in runners:
        raise RuntimeError(f"Runner '{runner_name}' not found in config")
    template = runners[runner_name]["command"]
    return template.format(prompt=str(prompt_path))


def preflight(project_root: Path, logs_dir: Path, runners: dict, tasks: list, phase: str):
    errors = []

    if shutil.which("git") is None:
        errors.append("git is not available on PATH")

    # ensure logs dir writable
    try:
        logs_dir.mkdir(parents=True, exist_ok=True)
        probe = logs_dir / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"logs_dir is not writable: {logs_dir} ({exc})")

    # check binaries only for runners used by selected tasks
    required_runners = set()
    for task in tasks:
        if task.get("phase", "main") != phase:
            continue
        required_runners.add(task.get("runner", "codex"))

    for name in sorted(required_runners):
        cfg = runners.get(name)
        if not cfg:
            errors.append(f"Runner '{name}' not found in config")
            continue
        cmd = cfg.get("command")
        if not cmd:
            errors.append(f"Runner '{name}' has empty command")
            continue
        try:
            first = shlex.split(cmd, posix=True)[0]
        except ValueError:
            errors.append(f"Runner '{name}' command cannot be parsed: {cmd}")
            continue
        if first in {"bash", "sh", "zsh"}:
            continue
        if shutil.which(first) is None:
            errors.append(f"Runner '{name}' binary not found on PATH: {first}")

    # check tasks: prompt exists, worktree path is free or a git worktree
    preflight_run_id = "preflight"
    worktrees_seen = {}
    branches_seen = {}
    logs_seen = {}
    for task in tasks:
        if task.get("phase", "main") != phase:
            continue
        if task.get("interactive") and not sys.stdin.isatty():
            errors.append(f"Interactive task '{task['name']}' requires a TTY")
        runner_name = task.get("runner", "codex")
        if runner_name not in runners:
            errors.append(f"Task '{task['name']}' uses unknown runner '{runner_name}'")
        worktree_value = format_template(
            task["worktree"],
            run_id=preflight_run_id,
            phase=phase,
            task=task["name"],
        )
        worktree = resolve_path(worktree_value, project_root)
        worktree_key = str(worktree)
        if worktree_key in worktrees_seen:
            errors.append(
                "Worktree path collision between "
                f"'{worktrees_seen[worktree_key]}' and '{task['name']}': {worktree}"
            )
        else:
            worktrees_seen[worktree_key] = task["name"]
        branch_value = format_template(
            task.get("branch", f"task/{task['name']}"),
            run_id=preflight_run_id,
            phase=phase,
            task=task["name"],
        )
        if branch_value in branches_seen:
            errors.append(
                "Branch collision between "
                f"'{branches_seen[branch_value]}' and '{task['name']}': {branch_value}"
            )
        else:
            branches_seen[branch_value] = task["name"]
        if worktree.exists() and not is_git_worktree(worktree):
            errors.append(
                f"Worktree path exists and is not a git worktree: {worktree}"
            )
        elif worktree.exists() and not is_same_git_repo(project_root, worktree):
            errors.append(
                "Worktree path exists but belongs to a different git repository: "
                f"{worktree}"
            )
        prompt_path = resolve_path(task["prompt"], project_root)
        if not prompt_path.exists():
            errors.append(f"Prompt file not found: {prompt_path}")
        elif prompt_path.is_dir():
            errors.append(f"Prompt path is a directory: {prompt_path}")
        log_value = task.get("log")
        if log_value:
            log_value = format_template(
                log_value,
                run_id=preflight_run_id,
                phase=phase,
                task=task["name"],
            )
            log_path = resolve_path(log_value, project_root)
        else:
            log_path = logs_dir / f"{task['name']}.log"
        log_key = str(log_path)
        if log_key in logs_seen:
            errors.append(
                f"Log path collision between '{logs_seen[log_key]}' and '{task['name']}': {log_path}"
            )
        else:
            logs_seen[log_key] = task["name"]
        if log_path.exists() and log_path.is_dir():
            errors.append(f"Log path is a directory: {log_path}")

    if errors:
        raise RuntimeError("Preflight failed:\n- " + "\n- ".join(errors))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="framework/orchestrator/orchestrator.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--phase",
        choices=["discovery", "main", "post", "legacy"],
        default="main",
    )
    parser.add_argument("--include-manual", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    cfg = load_config(config_path)

    config_dir = config_path.parent
    project_root = resolve_path(cfg.get("project_root", "."), config_dir)
    if not project_root.exists():
        raise RuntimeError(f"project_root does not exist: {project_root}")
    if not is_git_repo(project_root):
        raise RuntimeError(f"project_root is not a git repository: {project_root}")

    # Keep Codex session data inside the project unless explicitly overridden.
    os.environ.setdefault("CODEX_HOME", str(resolve_path("framework/.codex", project_root)))

    runners = cfg.get("runners", {})
    if bool_from_env(os.getenv("FRAMEWORK_RUNNER_NOOP")):
        for name in list(runners.keys()):
            runners[name]["command"] = 'cat "{prompt}" > /dev/null'
        print("[PREFLIGHT] FRAMEWORK_RUNNER_NOOP=1 — runner commands set to no-op")
    tasks, _ = normalize_tasks(cfg.get("tasks", []))
    tasks = select_tasks(tasks, args.phase, args.include_manual)

    if not tasks:
        raise RuntimeError(f"No tasks selected for phase '{args.phase}'")

    task_labels = []
    for task in tasks:
        suffix = " (manual)" if task.get("manual") else ""
        task_labels.append(f"{task['name']}{suffix}")
    print(f"[PHASE] {args.phase} | tasks: {', '.join(task_labels)}")

    logs_dir = resolve_path(cfg.get("logs_dir", "logs"), project_root)
    preflight(project_root, logs_dir, runners, tasks, args.phase)
    logs_dir.mkdir(parents=True, exist_ok=True)

    running = {}
    completed = {}
    blocked = {}
    paused_tasks = set()

    run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_started_at = time.time()
    framework_version = get_framework_version(project_root)
    events_path = logs_dir / "framework-run.jsonl"
    lock_path = logs_dir / "framework-run.lock"
    status_log_path = logs_dir / "protocol-status.log"
    lock_created = False
    progress_interval = float(os.getenv("FRAMEWORK_PROGRESS_INTERVAL", "10"))
    if progress_interval <= 0:
        progress_interval = None
    last_progress_at = run_started_at

    if args.phase in ("post", "legacy") and lock_path.exists():
        raise RuntimeError(
            f"Active run lock detected at {lock_path}. Finish the main run first."
        )

    if args.phase == "main" and not args.dry_run:
        lock_payload = {
            "run_id": run_id,
            "phase": args.phase,
            "started_at": iso_ts(run_started_at),
        }
        lock_path.write_text(json.dumps(lock_payload, ensure_ascii=True), encoding="utf-8")
        lock_created = True

    write_event(
        events_path,
        {
            "event": "run_start",
            "run_id": run_id,
            "phase": args.phase,
            "timestamp": iso_ts(run_started_at),
            "project_root": str(project_root),
            "config": str(config_path),
            "framework_version": framework_version,
            "tasks_total": len(tasks),
        },
    )

    def can_start(task):
        return all(dep in completed and completed[dep] == 0 for dep in task["depends_on"])

    framework_root = Path(__file__).resolve().parents[1]
    run_error = None
    try:
        while len(completed) + len(blocked) < len(tasks):
            progress = False
            for task in tasks:
                if task["name"] in running or task["name"] in completed:
                    continue
                if task["name"] in blocked:
                    continue

                failed_deps = [
                    dep
                    for dep in task["depends_on"]
                    if dep in blocked or (dep in completed and completed[dep] != 0)
                ]
                if failed_deps:
                    blocked[task["name"]] = failed_deps
                    print(f"[BLOCKED] {task['name']} <- {', '.join(failed_deps)}")
                    progress = True
                    continue
                if not can_start(task):
                    continue

                worktree_value = format_template(
                    task["worktree"],
                    run_id=run_id,
                    phase=args.phase,
                    task=task["name"],
                )
                worktree = resolve_path(worktree_value, project_root)
                branch_value = format_template(
                    task.get("branch", f"task/{task['name']}"),
                    run_id=run_id,
                    phase=args.phase,
                    task=task["name"],
                )
                branch = branch_value
                prompt_path = resolve_path(task["prompt"], project_root)
                if not prompt_path.exists():
                    raise RuntimeError(f"Prompt file not found: {prompt_path}")
                command = build_command(runners, task, prompt_path)
                interactive = bool(task.get("interactive"))
                log_value = task.get("log")
                if log_value:
                    log_value = format_template(
                        log_value,
                        run_id=run_id,
                        phase=args.phase,
                        task=task["name"],
                    )
                    log_path = resolve_path(log_value, project_root)
                else:
                    log_path = logs_dir / f"{task['name']}.log"
                pause_marker = None
                resume_interactive = False
                if interactive:
                    pause_value = task.get("pause_marker", f"framework/logs/{task['name']}.pause")
                    pause_value = format_template(
                        pause_value,
                        run_id=run_id,
                        phase=args.phase,
                        task=task["name"],
                    )
                    pause_marker = resolve_path(pause_value, project_root)
                    if pause_marker.exists():
                        resume_interactive = True
                        pause_marker.unlink()

                write_event(
                    events_path,
                    {
                        "event": "task_start",
                        "run_id": run_id,
                        "task": task["name"],
                        "timestamp": iso_ts(time.time()),
                        "command": command,
                        "branch": branch,
                        "worktree": str(worktree),
                        "log": str(log_path),
                        "interactive": interactive,
                        "pause_marker": str(pause_marker) if pause_marker else None,
                        "resume": resume_interactive,
                    },
                )

                if not args.dry_run:
                    ensure_worktree(project_root, worktree, branch)
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                    if interactive:
                        print(f"[START] {task['name']} (interactive) -> {log_path}")
                        cmd_name = ""
                        if isinstance(command, str):
                            parts = shlex.split(command)
                            if parts:
                                cmd_name = parts[0]
                        elif command:
                            cmd_name = command[0]
                        interactive_pref = os.environ.get("FRAMEWORK_INTERACTIVE", "").strip().lower()
                        script_path = shutil.which("script")
                        use_attach = (
                            cmd_name == "codex"
                            and sys.stdin.isatty()
                            and interactive_pref != "pty"
                            and script_path is not None
                        )
                        if use_attach:
                            print(
                                "[INTERACTIVE] Discovery started. Interactive session attached to this terminal."
                            )
                            if resume_interactive:
                                attach_cmd = ["codex", "resume", "--last"]
                            else:
                                prompt_text = prompt_path.read_text(
                                    encoding="utf-8", errors="ignore"
                                ).rstrip()
                                attach_cmd = ["codex", prompt_text]
                            cmd = [script_path, "-q"]
                            if resume_interactive:
                                cmd.append("-a")
                            cmd.append(str(log_path))
                            cmd += attach_cmd
                            proc = subprocess.Popen(cmd, cwd=worktree)
                        else:
                            print("[INTERACTIVE] Discovery started. Waiting for agent output...")
                            runner = framework_root / "tools" / "interactive-runner.py"
                            cmd = [
                                sys.executable,
                                str(runner),
                                "--transcript",
                                str(log_path),
                                "--prompt-file",
                                str(prompt_path),
                            ]
                            if pause_marker:
                                cmd += ["--pause-marker", str(pause_marker)]
                            if resume_interactive:
                                cmd.append("--append")
                            if cmd_name == "codex":
                                cmd += ["--prompt-mode", "arg"]
                            cmd += ["--", command]
                            proc = subprocess.Popen(cmd, cwd=worktree)
                        running[task["name"]] = (proc, None, log_path, interactive, pause_marker)
                    else:
                        log_f = open(log_path, "w", encoding="utf-8")
                        print(f"[START] {task['name']} -> {log_path}")
                        proc = subprocess.Popen(
                            command,
                            cwd=worktree,
                            shell=True,
                            stdout=log_f,
                            stderr=subprocess.STDOUT,
                        )
                        running[task["name"]] = (proc, log_f, log_path, interactive, pause_marker)
                else:
                    print(f"[DRY-RUN] {task['name']} in {worktree} :: {command}")
                    completed[task["name"]] = 0
                progress = True
                last_progress_at = time.time()

            to_remove = []
            for name, (proc, log_f, log_path, interactive, pause_marker) in running.items():
                ret = proc.poll()
                if ret is not None:
                    if log_f:
                        log_f.close()
                    paused = False
                    if interactive and pause_marker and pause_marker.exists():
                        paused = True
                    elif interactive and pause_marker and ret == 130:
                        write_pause_marker(pause_marker, "SIGINT")
                        paused = True
                    if paused:
                        paused_tasks.add(name)
                        completed[name] = 2
                    else:
                        completed[name] = ret
                    exit_code = 2 if paused else ret
                    print(f"[DONE] {name} exit={exit_code}")
                    write_event(
                        events_path,
                        {
                            "event": "task_end",
                            "run_id": run_id,
                            "task": name,
                            "timestamp": iso_ts(time.time()),
                            "exit_code": exit_code,
                            "paused": paused,
                        },
                    )
                    to_remove.append(name)
                    progress = True
                    last_progress_at = time.time()

            for name in to_remove:
                running.pop(name, None)

            if not progress and not running:
                pending = [
                    task["name"]
                    for task in tasks
                    if task["name"] not in completed and task["name"] not in blocked
                ]
                raise RuntimeError(
                    "No runnable tasks remaining. Check for cyclic dependencies: "
                    + ", ".join(pending)
                )

            now = time.time()
            if running and progress_interval and now - last_progress_at >= progress_interval:
                names = ", ".join(sorted(running.keys()))
                elapsed = format_duration(now - run_started_at)
                line = f"[RUNNING] {names} (elapsed {elapsed})"
                if any(item[3] for item in running.values()):
                    status_log_path.parent.mkdir(parents=True, exist_ok=True)
                    with status_log_path.open("a", encoding="utf-8") as f:
                        f.write(f"{iso_ts(time.time())} {line}\n")
                else:
                    print(line)
                last_progress_at = now

            time.sleep(1)
    except Exception as exc:
        run_error = str(exc)
        print(f"[ERROR] {run_error}")
    finally:
        if lock_created and lock_path.exists():
            lock_path.unlink()

    docs_dir = project_root / "framework" / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    summary_latest = docs_dir / "orchestrator-run-summary.md"
    summary_run = docs_dir / f"orchestrator-run-summary-{args.phase}-{run_id}.md"
    run_finished_at = time.time()

    def write_summary(path: Path, include_pointer: bool = False) -> None:
        with path.open("w", encoding="utf-8") as f:
            f.write("# Orchestrator Run Summary\n\n")
            f.write(f"- Run ID: {run_id}\n")
            f.write(f"- Phase: {args.phase}\n")
            f.write(f"- Started: {iso_ts(run_started_at)}\n")
            f.write(f"- Finished: {iso_ts(run_finished_at)}\n")
            f.write(f"- Framework version: {framework_version}\n")
            if include_pointer:
                f.write(f"- Summary file: {summary_run.name}\n")
            f.write("\n")
            if run_error:
                f.write(f"- Error: {run_error}\n\n")
            for task in tasks:
                name = task["name"]
                if name in completed:
                    code = completed[name]
                    if name in paused_tasks:
                        status = "PAUSED"
                    else:
                        status = "OK" if code == 0 else f"FAIL ({code})"
                else:
                    deps = blocked.get(name, [])
                    status = f"BLOCKED (deps: {', '.join(deps)})"
                f.write(f"- {name}: {status}\n")

    write_summary(summary_run, include_pointer=False)
    write_summary(summary_latest, include_pointer=True)

    write_event(
        events_path,
        {
            "event": "run_end",
            "run_id": run_id,
            "phase": args.phase,
            "timestamp": iso_ts(run_finished_at),
            "duration_sec": round(run_finished_at - run_started_at, 2),
            "completed": completed,
            "blocked": blocked,
            "paused": sorted(paused_tasks),
            "error": run_error,
        },
    )

    non_pause_failures = any(code not in (0, 2) for code in completed.values())
    failed_run = bool(blocked or run_error or non_pause_failures)
    agent_flow = bool_from_env(os.getenv("FRAMEWORK_AGENT_FLOW"))

    print(f"Summary saved to {summary_run}")
    if args.phase == "legacy":
        if agent_flow:
            print("Next: start the discovery interview in Codex (say \"start\").")
        else:
            print("Next: start the discovery interview:")
            print("  python3 framework/orchestrator/orchestrator.py --phase discovery")
    elif args.phase == "discovery":
        if paused_tasks:
            print("Discovery paused. Re-run to continue:")
            print("  ./install-framework.sh")
        elif failed_run:
            print("Discovery failed. Check logs and summary for details:")
            print(f"  {summary_run}")
        else:
            print("Discovery complete. Review the generated spec, then confirm start of development:")
            print("  python3 framework/orchestrator/orchestrator.py --phase main")
    publish_error = None
    try:
        if not args.dry_run:
            publish_error = maybe_publish_report(
                cfg, args.phase, run_id, framework_root, framework_version
            )
    except Exception as exc:
        publish_error = str(exc)
        print(f"[REPORT] {publish_error}")

    if publish_error:
        write_event(
            events_path,
            {
                "event": "report_publish_error",
                "run_id": run_id,
                "phase": args.phase,
                "timestamp": iso_ts(time.time()),
                "error": publish_error,
            },
        )
    exit_code = 0
    if failed_run:
        exit_code = 1
    elif paused_tasks:
        exit_code = 2
    sys.exit(exit_code)


def bool_from_env(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def parse_phases(value, default):
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def maybe_publish_report(cfg, phase, run_id, framework_root: Path, framework_version: str):
    reporting = cfg.get("reporting") or {}
    enabled = bool_from_env(os.getenv("FRAMEWORK_REPORTING_ENABLED"), reporting.get("enabled", False))
    if not enabled:
        return None

    phases = parse_phases(
        os.getenv("FRAMEWORK_REPORTING_PHASES"),
        reporting.get("phases", ["legacy", "discovery", "post", "main"]),
    )
    if phase not in phases:
        return None

    repo = os.getenv("FRAMEWORK_REPORTING_REPO", reporting.get("repo"))
    if not repo:
        return "FRAMEWORK_REPORTING_REPO is required"

    mode = os.getenv("FRAMEWORK_REPORTING_MODE", reporting.get("mode", "pr"))
    host_id = os.getenv("FRAMEWORK_REPORTING_HOST_ID", reporting.get("host_id", "unknown-host"))

    include_migration = bool_from_env(
        os.getenv("FRAMEWORK_REPORTING_INCLUDE_MIGRATION"),
        reporting.get("include_migration", phase == "legacy"),
    )
    include_review = bool_from_env(
        os.getenv("FRAMEWORK_REPORTING_INCLUDE_REVIEW"),
        reporting.get("include_review", False),
    )
    include_task_logs = bool_from_env(
        os.getenv("FRAMEWORK_REPORTING_INCLUDE_TASK_LOGS"),
        reporting.get("include_task_logs", False),
    )
    dry_run = bool_from_env(
        os.getenv("FRAMEWORK_REPORTING_DRY_RUN"),
        reporting.get("dry_run", False),
    )

    publish_script = framework_root / "tools" / "publish-report.py"
    if not publish_script.exists():
        return f"Publish script not found: {publish_script}"

    cmd = [
        "python3",
        str(publish_script),
        "--repo",
        repo,
        "--run-id",
        run_id,
        "--host-id",
        host_id,
        "--mode",
        mode,
        "--phase",
        phase,
        "--framework-version",
        framework_version,
    ]
    if include_migration:
        cmd.append("--include-migration")
    if include_review:
        cmd.append("--include-review")
    if include_task_logs:
        cmd.append("--include-task-logs")
    if dry_run:
        cmd.append("--dry-run")

    res = subprocess.run(cmd, check=False, text=True, capture_output=True)
    if res.returncode != 0:
        return res.stderr or res.stdout or "Report publish failed"
    if res.stdout:
        print(res.stdout.strip())
    return None


if __name__ == "__main__":
    main()
