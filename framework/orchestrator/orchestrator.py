#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML is required. Install with: pip install pyyaml")
    sys.exit(1)


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, shell=True, check=False)


def resolve_path(value, base: Path) -> Path:
    path = value if isinstance(value, Path) else Path(value)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


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


def ensure_worktree(project_root: Path, worktree_path: Path, branch: str):
    if worktree_path.exists():
        if not is_git_worktree(worktree_path):
            raise RuntimeError(
                f"Worktree path exists but is not a git worktree: {worktree_path}"
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
        tasks_by_name[name] = task
        ordered.append(task)
    for name, task in tasks_by_name.items():
        for dep in task["depends_on"]:
            if dep not in tasks_by_name:
                raise RuntimeError(f"Task '{name}' depends on unknown task '{dep}'")
    return ordered, tasks_by_name


def build_command(runners, task, prompt_path: Path):
    runner_name = task.get("runner", "codex")
    if runner_name not in runners:
        raise RuntimeError(f"Runner '{runner_name}' not found in config")
    template = runners[runner_name]["command"]
    return template.format(prompt=str(prompt_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="framework/orchestrator/orchestrator.yaml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    cfg = load_config(config_path)

    config_dir = config_path.parent
    project_root = resolve_path(cfg.get("project_root", "."), config_dir)
    if not project_root.exists():
        raise RuntimeError(f"project_root does not exist: {project_root}")
    if not is_git_repo(project_root):
        raise RuntimeError(f"project_root is not a git repository: {project_root}")

    logs_dir = resolve_path(cfg.get("logs_dir", "logs"), project_root)
    logs_dir.mkdir(parents=True, exist_ok=True)

    runners = cfg.get("runners", {})
    tasks, _ = normalize_tasks(cfg.get("tasks", []))

    running = {}
    completed = {}
    blocked = {}

    def can_start(task):
        return all(dep in completed and completed[dep] == 0 for dep in task["depends_on"])

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

            worktree = resolve_path(task["worktree"], project_root)
            branch = task.get("branch", f"task/{task['name']}")
            prompt_path = resolve_path(task["prompt"], project_root)
            if not prompt_path.exists():
                raise RuntimeError(f"Prompt file not found: {prompt_path}")
            command = build_command(runners, task, prompt_path)
            log_value = task.get("log")
            if log_value:
                log_path = resolve_path(log_value, project_root)
            else:
                log_path = logs_dir / f"{task['name']}.log"

            if not args.dry_run:
                ensure_worktree(project_root, worktree, branch)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                log_f = open(log_path, "w", encoding="utf-8")
                print(f"[START] {task['name']} -> {log_path}")
                proc = subprocess.Popen(
                    command,
                    cwd=worktree,
                    shell=True,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                )
                running[task["name"]] = (proc, log_f, log_path)
            else:
                print(f"[DRY-RUN] {task['name']} in {worktree} :: {command}")
                completed[task["name"]] = 0
            progress = True

        to_remove = []
        for name, (proc, log_f, log_path) in running.items():
            ret = proc.poll()
            if ret is not None:
                log_f.close()
                completed[name] = ret
                print(f"[DONE] {name} exit={ret}")
                to_remove.append(name)
                progress = True

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

        time.sleep(1)

    summary_path = project_root / "docs" / "orchestrator-run-summary.md"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as f:
        f.write("# Orchestrator Run Summary\n\n")
        for task in tasks:
            name = task["name"]
            if name in completed:
                code = completed[name]
                status = "OK" if code == 0 else f"FAIL ({code})"
            else:
                deps = blocked.get(name, [])
                status = f"BLOCKED (deps: {', '.join(deps)})"
            f.write(f"- {name}: {status}\n")

    print(f"Summary saved to {summary_path}")
    exit_code = 0
    if any(code != 0 for code in completed.values()) or blocked:
        exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
