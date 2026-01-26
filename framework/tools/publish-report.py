#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORT_SCRIPT = ROOT / "tools" / "export-report.py"


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=False, text=True, capture_output=True)


def ensure_zip(
    path: Path,
    run_id: str,
    include_migration: bool,
    include_review: bool,
    include_task_logs: bool,
):
    if path and path.exists():
        return path
    args = ["python3", str(EXPORT_SCRIPT), "--run-id", run_id]
    if include_migration:
        args.append("--include-migration")
    if include_review:
        args.append("--include-review")
    if include_task_logs:
        args.append("--include-task-logs")
    res = run(args)
    if res.returncode != 0:
        raise RuntimeError(res.stderr or res.stdout)
    default_zip = ROOT / "outbox" / f"report-{run_id}.zip"
    if not default_zip.exists():
        raise RuntimeError("Export did not produce report zip")
    return default_zip


def github_request(token: str, method: str, url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    cmd = [
        "curl",
        "-sS",
        "-X",
        method,
        "-H",
        f"Authorization: token {token}",
        "-H",
        "Content-Type: application/json",
        url,
        "-d",
        data.decode("utf-8"),
    ]
    res = run(cmd)
    if res.returncode != 0:
        raise RuntimeError(res.stderr or res.stdout)
    return res.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish framework report bundle to GitHub.")
    parser.add_argument("--repo", required=True, help="Target repo, e.g. owner/name")
    parser.add_argument("--run-id", default="unknown")
    parser.add_argument("--zip", dest="zip_path")
    parser.add_argument("--host-id", default="unknown-host")
    parser.add_argument("--phase", default="unknown")
    parser.add_argument("--framework-version", default="unknown")
    parser.add_argument("--mode", choices=["pr", "issue", "both"], default="pr")
    parser.add_argument("--base", default="main")
    parser.add_argument("--include-migration", action="store_true")
    parser.add_argument("--include-review", action="store_true")
    parser.add_argument("--include-task-logs", action="store_true")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"))
    args = parser.parse_args()

    if not args.token:
        raise SystemExit("GITHUB_TOKEN is required")

    run_id = args.run_id
    zip_path = Path(args.zip_path) if args.zip_path else None
    zip_path = ensure_zip(
        zip_path,
        run_id,
        args.include_migration,
        args.include_review,
        args.include_task_logs,
    )

    branch = f"reports/{args.host_id}/{run_id}"
    report_path = Path("reports") / args.host_id / f"report-{run_id}.zip"

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_dir = Path(tmpdir) / "repo"
        clone_url = f"https://{args.token}@github.com/{args.repo}.git"
        res = run(["git", "clone", "--depth", "1", clone_url, str(repo_dir)])
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)

        res = run(["git", "checkout", "-b", branch], cwd=repo_dir)
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)

        dest = repo_dir / report_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(zip_path, dest)

        res = run(["git", "add", str(report_path)], cwd=repo_dir)
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)

        commit_msg = f"Add report {run_id} from {args.host_id}"
        res = run(["git", "commit", "-m", commit_msg], cwd=repo_dir)
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)

        res = run(["git", "push", "-u", "origin", branch], cwd=repo_dir)
        if res.returncode != 0:
            raise RuntimeError(res.stderr or res.stdout)

    pr_url = None
    issue_url = None
    api_base = f"https://api.github.com/repos/{args.repo}"
    report_body = "\n".join(
        [
            "## Report Metadata",
            f"- Host ID: {args.host_id}",
            f"- Run ID: {run_id}",
            f"- Phase: {args.phase}",
            f"- Framework version: {args.framework_version}",
            f"- Bundle path: `{report_path}`",
            "",
            "## Next Steps",
            "- Use the bug report template at `framework/docs/reporting/bug-report-template.md`.",
            "- Attach relevant logs or point to the report bundle above.",
        ]
    )

    if args.mode in ("pr", "both"):
        payload = {
            "title": f"Report {run_id} from {args.host_id}",
            "head": branch,
            "base": args.base,
            "body": report_body,
        }
        pr_url = json.loads(github_request(args.token, "POST", f"{api_base}/pulls", payload)).get("html_url")

    if args.mode in ("issue", "both"):
        payload = {
            "title": f"Report {run_id} from {args.host_id}",
            "body": report_body + f"\n\nBranch: `{branch}`.",
        }
        issue_url = json.loads(github_request(args.token, "POST", f"{api_base}/issues", payload)).get("html_url")

    if pr_url:
        print(f"PR created: {pr_url}")
    if issue_url:
        print(f"Issue created: {issue_url}")


if __name__ == "__main__":
    main()
