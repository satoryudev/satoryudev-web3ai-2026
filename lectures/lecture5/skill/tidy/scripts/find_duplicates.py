#!/usr/bin/env python3
"""Find probable duplicate files by content hash and by name pattern.

Usage:
  python find_duplicates.py <directory> [--max-size-mb 200]

Two kinds of duplicates surface:

  hash_groups  — byte-identical files (sha256 match). Definitely duplicates.
  name_groups  — files whose names imply duplication ("X のコピー.pdf",
                 "X (3).pdf", "X copy.pdf") but whose content differs or
                 wasn't hashed. Suspicious; the user should glance at them.

Files larger than --max-size-mb are not hashed (skipping avoids minute-long
stalls on backup ZIPs). They still show up in name_groups if their names match
the copy patterns.

Output is structured JSON so the agent can build a deletion-free move plan
that quarantines extras under _tidy_review/duplicates/.
"""
import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# Patterns we accept as "this file is a copy of something else." The leading
# whitespace tolerance matters because macOS Finder, Windows Explorer, and
# JP apps all produce slightly different artifacts.
COPY_PATTERNS = [
    re.compile(r"\s*のコピー(?:\s*\d+)?(?=\.[^.]*$)"),  # "X のコピー.ext"
    re.compile(r"\s+copy(?:\s*\d+)?(?=\.[^.]*$)", re.IGNORECASE),  # "X copy.ext"
    re.compile(r"\s*\(\d+\)(?=\.[^.]*$)"),  # "X (3).ext"
    re.compile(r"\s*-\s*copy(?=\.[^.]*$)", re.IGNORECASE),  # "X - copy.ext"
]

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
}


def sha256(path: Path, chunk: int = 1 << 16) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for blk in iter(lambda: f.read(chunk), b""):
            h.update(blk)
    return h.hexdigest()


def canonical_name(name: str) -> str:
    """Strip copy markers to get a key for grouping suspected duplicates."""
    out = name
    for p in COPY_PATTERNS:
        out = p.sub("", out)
    return out.lower()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("directory")
    ap.add_argument(
        "--max-size-mb",
        type=int,
        default=200,
        help="skip hashing files larger than this many MB (still considered for name patterns)",
    )
    args = ap.parse_args()
    root = Path(args.directory).resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        sys.exit(1)
    max_bytes = args.max_size_mb * 1024 * 1024

    by_hash: dict[str, list[dict]] = defaultdict(list)
    by_canonical: dict[str, list[dict]] = defaultdict(list)
    skipped: list[dict] = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(p in SKIP_NAMES for p in path.parts):
            continue
        try:
            st = path.stat()
        except OSError:
            continue
        info = {"path": str(path), "size": st.st_size, "name": path.name}

        # always record by canonical name (lightweight)
        by_canonical[canonical_name(path.name)].append(info)

        # only hash if not too large
        if st.st_size > max_bytes:
            skipped.append({**info, "reason": "too large to hash"})
            continue
        try:
            digest = sha256(path)
        except OSError as e:
            skipped.append({**info, "reason": str(e)})
            continue
        by_hash[digest].append(info)

    hash_groups = [
        {"hash": h, "files": files, "wasted_bytes": sum(f["size"] for f in files) - files[0]["size"]}
        for h, files in by_hash.items()
        if len(files) > 1
    ]
    hash_paths = {f["path"] for g in hash_groups for f in g["files"]}

    # Suppress name-pattern groups whose files are already grouped by content
    # hash — that would be double-counting.
    name_groups = []
    for canonical, files in by_canonical.items():
        remaining = [f for f in files if f["path"] not in hash_paths]
        if len(remaining) > 1:
            name_groups.append({"canonical": canonical, "files": remaining})

    result = {
        "root": str(root),
        "hash_groups": hash_groups,
        "name_groups": name_groups,
        "skipped": skipped,
        "summary": {
            "hash_group_count": len(hash_groups),
            "name_group_count": len(name_groups),
            "total_wasted_bytes": sum(g["wasted_bytes"] for g in hash_groups),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
