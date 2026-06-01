#!/usr/bin/env python3
"""Apply a Tidy move plan with journaling.

Plan format (JSON):
  {
    "moves": [
      {"from": "/abs/src.pdf", "to": "/abs/dest/dir/src.pdf"},
      ...
    ]
  }

Usage:
  python apply_plan.py <plan.json>           # dry-run (default)
  python apply_plan.py <plan.json> --apply   # actually move files

Why this script exists: agents are bad at doing the "validate everything,
THEN act, and write a journal as you go" dance reliably. Centralizing those
rules here means any consumer of this skill gets the same safety floor:

  * sources must exist
  * destinations must NOT exist (refuse to overwrite)
  * every move is journaled to .tidy-journal.jsonl in the destination root,
    making undo a one-liner.

If anything fails mid-apply, the journal is your audit trail.
"""
import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path


def common_ancestor(paths):
    """Return the deepest directory that is a parent of every path in paths."""
    if not paths:
        return None
    parts_list = [Path(p).resolve().parts for p in paths]
    common = []
    for tup in zip(*parts_list):
        if all(p == tup[0] for p in tup):
            common.append(tup[0])
        else:
            break
    if not common:
        return Path("/")
    # If common path is a file, take its parent.
    candidate = Path(*common)
    return candidate if candidate.is_dir() else candidate.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan", help="path to plan JSON")
    ap.add_argument(
        "--apply",
        action="store_true",
        help="actually perform moves; without this flag, dry-run only",
    )
    args = ap.parse_args()

    plan_path = Path(args.plan)
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"error reading plan: {e}", file=sys.stderr)
        sys.exit(1)

    moves = plan.get("moves", [])
    if not moves:
        print("plan has no moves", file=sys.stderr)
        sys.exit(1)

    # --- validation pass (always run, even in dry-run) ---
    errors = []
    for i, m in enumerate(moves):
        if "from" not in m or "to" not in m:
            errors.append(f"move[{i}]: missing 'from' or 'to'")
            continue
        src = Path(m["from"])
        dst = Path(m["to"])
        if not src.exists():
            errors.append(f"move[{i}]: source not found: {src}")
        if dst.exists():
            errors.append(f"move[{i}]: destination already exists (refusing): {dst}")
        if src.resolve() == dst.resolve():
            errors.append(f"move[{i}]: source and destination are the same: {src}")

    if errors:
        print("validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(2)

    if not args.apply:
        print(f"DRY RUN — would move {len(moves)} files:")
        for m in moves[:30]:
            print(f"  {m['from']}\n    → {m['to']}")
        if len(moves) > 30:
            print(f"  ... and {len(moves) - 30} more")
        print("\nRe-run with --apply to execute.")
        return

    # --- apply ---
    destinations = [Path(m["to"]) for m in moves]
    ancestor = common_ancestor(destinations)
    journal_dir = ancestor if ancestor and ancestor.is_dir() else destinations[0].parent
    journal_path = journal_dir / ".tidy-journal.jsonl"

    ts = datetime.datetime.now().isoformat(timespec="seconds")
    applied = 0
    with journal_path.open("a", encoding="utf-8") as jf:
        # Write a session header so undo tooling can group moves by run.
        jf.write(
            json.dumps(
                {
                    "ts": ts,
                    "session": True,
                    "moves_planned": len(moves),
                    "cwd": os.getcwd(),
                },
                ensure_ascii=False,
            )
            + "\n"
        )
        for m in moves:
            src = Path(m["from"])
            dst = Path(m["to"])
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            jf.write(
                json.dumps(
                    {"ts": ts, "from": str(src), "to": str(dst)},
                    ensure_ascii=False,
                )
                + "\n"
            )
            applied += 1

    print(f"moved {applied} files.")
    print(f"journal: {journal_path}")
    print("undo hint: read the journal in reverse and shutil.move(to, from).")


if __name__ == "__main__":
    main()
