#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import tempfile
import time
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATH = ROOT / "VERSION"
SUMMARY_PATH = ROOT / "docs" / "orchestrator-run-summary.md"
DOCS_DIR = ROOT / "docs"
LOGS_DIR = ROOT / "logs"
REVIEW_DIR = ROOT / "review"
FRAMEWORK_REVIEW_DIR = ROOT / "framework-review"
MIGRATION_DIR = ROOT / "migration"
ORCH_DIR = ROOT / "orchestrator"
OUTBOX_DIR = ROOT / "outbox"
REPORTING_DIR = DOCS_DIR / "reporting"

SENSITIVE_PATTERNS = [
    # key=value or key: value (env/logs)
    (re.compile(r"(?i)\\b(api[-_ ]?key|token|secret|password|passwd|pwd|access[-_ ]?key|client[-_ ]?secret|private[-_ ]?key)\\b\\s*[:=]\\s*([^\\s\"'`]+)"), "kv"),
    # JSON style "key": "value"
    (re.compile(r"(?i)\"(api[-_ ]?key|token|secret|password|passwd|pwd|access[-_ ]?key|client[-_ ]?secret|private[-_ ]?key)\"\\s*:\\s*\"([^\"]+)\""), "json"),
    # Authorization/Bearer
    (re.compile(r"(?i)authorization\\s*[:=]\\s*(bearer\\s+)?([^\\s\"'`]+)"), "auth"),
    # AWS keys
    (re.compile(r"AKIA[0-9A-Z]{16}"), "fixed"),
    (re.compile(r"(?i)(aws_secret_access_key)\\s*[:=]\\s*([^\\s\"'`]+)"), "kv"),
    # JWT-like tokens
    (re.compile(r"eyJ[\\w-]{10,}\\.[\\w-]{10,}\\.[\\w-]{10,}"), "fixed"),
    # GitHub/Stripe/Supabase common tokens
    (re.compile(r"ghp_[0-9A-Za-z]{30,}"), "fixed"),
    (re.compile(r"github_pat_[0-9A-Za-z_]{20,}"), "fixed"),
    (re.compile(r"sk_live_[0-9a-zA-Z]{20,}"), "fixed"),
    (re.compile(r"sk_test_[0-9a-zA-Z]{20,}"), "fixed"),
    (re.compile(r"whsec_[0-9a-zA-Z]{20,}"), "fixed"),
]


def _redact_match(mode: str, match: re.Match) -> str:
    if mode == "kv":
        return f"{match.group(1)}: ***"
    if mode == "json":
        return f"\"{match.group(1)}\": \"***\""
    if mode == "auth":
        prefix = match.group(1) or ""
        return f"authorization: {prefix}***".strip()
    return "***"


def redact_text(text: str) -> str:
    for pattern, mode in SENSITIVE_PATTERNS:
        text = pattern.sub(lambda m: _redact_match(mode, m), text)
    if "PRIVATE KEY" in text:
        text = re.sub(
            r"-----BEGIN[^-]+-----[\s\S]*?-----END[^-]+-----",
            "<REDACTED PRIVATE KEY>",
            text,
        )
    return text


def parse_run_id() -> str:
    if SUMMARY_PATH.exists():
        for line in SUMMARY_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("- Run ID:"):
                return line.split(":", 1)[1].strip()
            if line.startswith("- Latest Run ID:"):
                return line.split(":", 1)[1].strip()
    jsonl = LOGS_DIR / "framework-run.jsonl"
    if jsonl.exists():
        run_id = None
        for line in jsonl.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if payload.get("event") == "run_end":
                run_id = payload.get("run_id") or run_id
        if run_id:
            return run_id
    return "unknown"


def is_under(path: Path, base: Path) -> bool:
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def copy_file(src: Path, dest: Path, redact: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if redact:
        text = src.read_text(encoding="utf-8", errors="ignore")
        dest.write_text(redact_text(text), encoding="utf-8")
    else:
        shutil.copy2(src, dest)


def add_tree(src_dir: Path, dest_dir: Path, redact: bool, collected: list) -> None:
    if not src_dir.exists():
        return
    for path in src_dir.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(src_dir)
        dest = dest_dir / rel
        copy_file(path, dest, redact=redact)
        collected.append(str(dest))


def main() -> None:
    parser = argparse.ArgumentParser(description="Export framework run reports as a zip bundle.")
    parser.add_argument("--run-id", help="Override run id")
    parser.add_argument("--out", help="Output zip path")
    parser.add_argument("--include-review", action="store_true", help="Include framework/review")
    parser.add_argument("--include-migration", action="store_true", help="Include framework/migration")
    parser.add_argument("--include-task-logs", action="store_true", help="Include framework/logs/*.log")
    parser.add_argument("--no-redact", action="store_true", help="Disable log redaction")
    args = parser.parse_args()

    run_id = args.run_id or parse_run_id()
    out_path = Path(args.out) if args.out else OUTBOX_DIR / f"report-{run_id}.zip"

    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)

    redact_logs = not args.no_redact

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        collected = []

        if SUMMARY_PATH.exists():
            copy_file(SUMMARY_PATH, tmp_root / "docs/orchestrator-run-summary.md", redact=False)
            collected.append(str(tmp_root / "docs/orchestrator-run-summary.md"))
        if DOCS_DIR.exists():
            for path in DOCS_DIR.glob("orchestrator-run-summary-*.md"):
                copy_file(path, tmp_root / f"docs/{path.name}", redact=False)
                collected.append(str(tmp_root / f"docs/{path.name}"))

        if VERSION_PATH.exists():
            copy_file(VERSION_PATH, tmp_root / "VERSION", redact=False)
            collected.append(str(tmp_root / "VERSION"))

        jsonl = LOGS_DIR / "framework-run.jsonl"
        if jsonl.exists():
            copy_file(jsonl, tmp_root / "logs/framework-run.jsonl", redact=redact_logs)
            collected.append(str(tmp_root / "logs/framework-run.jsonl"))

        if args.include_task_logs and LOGS_DIR.exists():
            for path in LOGS_DIR.glob("*.log"):
                copy_file(path, tmp_root / f"logs/{path.name}", redact=redact_logs)
                collected.append(str(tmp_root / f"logs/{path.name}"))

        add_tree(FRAMEWORK_REVIEW_DIR, tmp_root / "framework-review", redact=False, collected=collected)

        if args.include_review:
            add_tree(REVIEW_DIR, tmp_root / "review", redact=False, collected=collected)

        if args.include_migration:
            add_tree(MIGRATION_DIR, tmp_root / "migration", redact=False, collected=collected)

        if ORCH_DIR.exists():
            add_tree(ORCH_DIR, tmp_root / "orchestrator", redact=False, collected=collected)
        if REPORTING_DIR.exists():
            add_tree(REPORTING_DIR, tmp_root / "docs/reporting", redact=False, collected=collected)

        manifest = {
            "run_id": run_id,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
            "redaction": "on" if redact_logs else "off",
            "included": sorted({str(Path(p).relative_to(tmp_root)) for p in collected}),
        }
        manifest_path = tmp_root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8")

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in tmp_root.rglob("*"):
                if path.is_dir():
                    continue
                zf.write(path, path.relative_to(tmp_root).as_posix())

    print(f"Report bundle created: {out_path}")


if __name__ == "__main__":
    main()
