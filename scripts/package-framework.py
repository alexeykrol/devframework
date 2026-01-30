#!/usr/bin/env python3
import argparse
import base64
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_DIR = ROOT / "framework"
VERSION_FILE = FRAMEWORK_DIR / "VERSION"
DEFAULT_OUT = ROOT / "framework.zip"
INSTALLER_PATH = ROOT / "install-framework.sh"
EXCLUDE_DIRS = {"logs", "outbox", "__pycache__"}
EXCLUDE_NAMES = {".DS_Store"}
EMBED_BEGIN = "__FRAMEWORK_ZIP_PAYLOAD_BEGIN__"
EMBED_END = "__FRAMEWORK_ZIP_PAYLOAD_END__"


def git_short():
    res = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        check=False,
        text=True,
        capture_output=True,
    )
    if res.returncode == 0:
        value = res.stdout.strip()
        return value or None
    return None


def should_skip(path: Path) -> bool:
    rel = path.relative_to(FRAMEWORK_DIR)
    for part in rel.parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_NAMES:
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Package framework/ into framework.zip")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output zip path")
    parser.add_argument("--version", help="Override version string")
    args = parser.parse_args()

    if not FRAMEWORK_DIR.exists():
        raise SystemExit(f"Missing framework dir: {FRAMEWORK_DIR}")

    if args.version:
        version = args.version
        VERSION_FILE.write_text(f"{version}\n", encoding="utf-8")
    elif VERSION_FILE.exists():
        version = VERSION_FILE.read_text(encoding="utf-8", errors="ignore").strip()
    else:
        version = git_short() or time.strftime("%Y%m%d%H%M%S")
        VERSION_FILE.write_text(f"{version}\n", encoding="utf-8")

    out_path = Path(args.out)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in FRAMEWORK_DIR.rglob("*"):
            if path.is_dir():
                continue
            if should_skip(path):
                continue
            arcname = path.relative_to(ROOT).as_posix()
            zf.write(path, arcname)

    print(f"Framework packaged: {out_path}")
    print(f"Version: {version}")

    if INSTALLER_PATH.exists():
        content_lines = INSTALLER_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()
        if EMBED_BEGIN in content_lines and EMBED_END in content_lines:
            payload = base64.b64encode(out_path.read_bytes()).decode("ascii")
            chunked = [payload[i:i + 76] for i in range(0, len(payload), 76)]
            start_idx = content_lines.index(EMBED_BEGIN)
            end_idx = content_lines.index(EMBED_END)
            if end_idx > start_idx:
                new_lines = content_lines[:start_idx + 1] + chunked + content_lines[end_idx:]
                INSTALLER_PATH.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                print(f"Installer updated with embedded zip: {INSTALLER_PATH}")
                timestamp = time.strftime("%Y%m%d%H%M%S")
                versioned = ROOT / f"install-fr-{version}-{timestamp}.sh"
                shutil.copy2(INSTALLER_PATH, versioned)
                print(f"Versioned installer: {versioned}")


if __name__ == "__main__":
    main()
