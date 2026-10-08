#!/usr/bin/env python
"""Package the LeRobot source + tutorials for a customer.

Excludes everything that belongs to THIS machine (virtualenv, build artifacts,
training outputs, caches) so the customer gets a clean copy they can install
and run from scratch using the tutorials.

Usage:
    python pack_for_customer.py            # -> D:\\Project\\lerobot-customer-package.zip
    python pack_for_customer.py --out C:\\pkg\\lerobot.zip
"""

import argparse
import zipfile
from pathlib import Path

# Project root (the directory this script lives in).
ROOT = Path(__file__).resolve().parent

# Directories / files that are machine-specific and must NOT ship.
EXCLUDE_DIRS = {
    ".venv", "venv", "env", "env.bak", "venv.bak",
    ".uv-cache", "uv-cache", "uv-python",
    "outputs", "build", "dist", "sdist", "wheels", "downloads", "eggs", ".eggs",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".mypy_cache",
    ".git", ".claude", ".idea", ".vscode", "node_modules",
    "htmlcov", ".coverage", "coverage",
}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".pyd", ".so", ".egg-info"}
EXCLUDE_FILES = {
    "pyvenv.cfg", "CACHEDIR.TAG", ".DS_Store", "Thumbs.db",
    # The packaging script itself is not needed in the delivered package.
    "pack_for_customer.py",
}


def is_excluded(rel_path: str, name: str) -> bool:
    """Return True if a single path component should be skipped."""
    if name in EXCLUDE_DIRS:
        return True
    if name in EXCLUDE_FILES:
        return True
    for suffix in EXCLUDE_SUFFIXES:
        if name.endswith(suffix):
            return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT.parent / "lerobot-customer-package.zip",
        help="Output zip path (default: <parent>/lerobot-customer-package.zip)",
    )
    args = parser.parse_args()

    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    included = 0
    skipped_dirs = 0

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ROOT.rglob("*")):
            # Compute path relative to ROOT using forward slashes for the archive.
            rel = path.relative_to(ROOT)
            parts = rel.parts
            if any(is_excluded(rel.as_posix(), part) for part in parts):
                if path.is_dir():
                    skipped_dirs += 1
                continue
            if path.is_dir():
                # Add an explicit directory entry so empty dirs are preserved.
                arcname = rel.as_posix() + "/"
                zf.writestr(arcname, "")
                continue
            if path.is_file():
                zf.write(path, rel.as_posix())
                included += 1

    total_mb = out.stat().st_size / (1024 * 1024)
    print(f"Packed {included} files, skipped {skipped_dirs} dirs.")
    print(f"Saved to: {out}  ({total_mb:.1f} MB)")


if __name__ == "__main__":
    main()
