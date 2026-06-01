#!/usr/bin/env python3
"""Scan a directory and emit a JSON manifest of files.

Usage:
  python scan_dir.py <directory> [--max-depth N] [--include-hidden]

Why this script exists: scanning with the right exclusions (.git, node_modules,
.DS_Store, .venv, .vercel) is something every Tidy invocation needs, and getting
it right inline every time is wasted effort and risk. Output is structured JSON
so the agent can pipe it through grep / jq or feed it back into apply_plan.
"""
import argparse
import json
import sys
from pathlib import Path

SKIP_NAMES = {
    ".git",
    "node_modules",
    ".DS_Store",
    "__pycache__",
    ".venv",
    ".vercel",
    ".next",
    "dist",
    "build",
    ".turbo",
    ".pytest_cache",
    ".mypy_cache",
}


def scan(root: Path, max_depth: int, include_hidden: bool):
    files = []
    root = root.resolve()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
        except ValueError:
            continue
        # depth limit (rel.parts counts the filename too, so a top-level file
        # has 1 part; --max-depth 1 means "only top-level").
        if len(rel.parts) > max_depth:
            continue
        # skip noise directories / files
        if any(p in SKIP_NAMES for p in rel.parts):
            continue
        if not include_hidden and any(p.startswith(".") for p in rel.parts):
            continue
        try:
            st = path.stat()
        except OSError:
            continue
        files.append(
            {
                "name": path.name,
                "path": str(path),
                "rel": str(rel),
                "size": st.st_size,
                "mtime": st.st_mtime,
                "ext": path.suffix.lower(),
            }
        )
    files.sort(key=lambda f: (f["rel"]))
    return files


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("directory", help="directory to scan")
    ap.add_argument(
        "--max-depth",
        type=int,
        default=2,
        help="how deep to recurse; default 2 (top level + one nested level)",
    )
    ap.add_argument(
        "--include-hidden",
        action="store_true",
        help="include dotfiles (off by default)",
    )
    args = ap.parse_args()
    root = Path(args.directory)
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        sys.exit(1)
    files = scan(root, args.max_depth, args.include_hidden)
    out = {
        "root": str(root.resolve()),
        "count": len(files),
        "total_bytes": sum(f["size"] for f in files),
        "files": files,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
