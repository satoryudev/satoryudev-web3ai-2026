---
name: tidy
description: Organize messy directories using AI categorization, natural-language search, and duplicate detection. Use this skill whenever the user asks to clean up, organize, sort, or tidy a folder (Desktop, Downloads, project directories), wants to find duplicate files, needs to search files with vague natural-language queries ("先月の請求書", "the report I wrote last week", "vacation photos"), or asks "where did I save X". Trigger even when the user does not say "tidy" or "organize" — phrases like "整理して", "デスクトップが散らかってる", "clean up my downloads", "find that file from last month", "重複ファイル消したい" all warrant invoking it. The skill always proposes changes as a dry-run plan first, never deletes files, and journals every move for reversibility.
---

# Tidy — AI File Organizer

Help users tame messy file collections by combining their existing file metadata (name, extension, size, mtime) with your understanding of file-naming conventions, dates, and the user's intent.

You are touching the user's personal data. A single wrong move erodes trust permanently — read the safety rules before acting.

## Three capabilities

Use independently or in combination:

1. **Organize** — scan a directory, propose a category tree (`Photos/2026-04/`, `Invoices/`, `Screenshots/`), and move files into it.
2. **Search** — given a natural-language query like "先月の請求書" or "the slide deck for the AWS pitch", find the most relevant files.
3. **Duplicates** — find probable duplicates by content hash and by name pattern (`foo.pdf` ↔ `foo のコピー.pdf` ↔ `foo (3).pdf`).

## Safety rules — non-negotiable

These exist because the cost of a wrong move (silent data loss, broken references) is much higher than the cost of an extra confirmation round.

- **Default to dry-run.** Always show the proposed plan first. Ask "適用していい？" before any move. Apply only on an explicit yes.
- **Never delete.** Duplicates and unknowns go to a sibling `_tidy_review/` folder, never `rm`.
- **Journal every move.** `apply_plan.py` writes `.tidy-journal.jsonl` recording `from → to` pairs, so undo is possible by reading the journal in reverse.
- **Respect dotfiles and system folders.** Skip `.git`, `node_modules`, `.DS_Store`, `__pycache__`, `Library/`, `System/`, `.venv`, `.vercel`.
- **Never operate above the working directory** unless the user explicitly hands you an absolute path outside it.
- **Refuse overwrites.** If a destination path already exists, stop and surface the conflict — don't silently rename.

## Workflow — Organize

When asked to organize / clean up / tidy a directory:

1. **Confirm scope.** Ask which directory if unclear. Default suggestion: the directory the user mentioned (`Desktop`, `Downloads`) or the current `pwd`.
2. **Scan.** Run `python scripts/scan_dir.py <target>` to get a JSON manifest with name, size, mtime, extension. (Pass `--max-depth 2` by default; deeper trees often hide structure the user wants to preserve.)
3. **Detect duplicates.** Run `python scripts/find_duplicates.py <target>` so the plan can include them.
4. **Propose a category tree.** Use the rubric in `references/categorization-rubric.md`. Categories must fit the actual file mix — don't force-create empty buckets.
5. **Print the plan.** Show as a tree with file counts per category and the duplicate count. Add a one-line rationale next to any non-obvious decision.
6. **Get explicit approval.** Wait for "OK"/"はい"/"yes". Anything else → revise.
7. **Execute.** Build a plan JSON (`{"moves": [{"from": ..., "to": ...}, ...]}`) and run `python scripts/apply_plan.py <plan.json> --apply`. The script refuses overwrites and writes the journal.

## Workflow — Search

When the user asks to find a file with a vague query:

1. **Scan** the directory with `scripts/scan_dir.py` (you can reuse `.tidy-manifest.json` if present and fresh).
2. **Pre-filter** with `grep` / `find` for any concrete tokens you can extract from the query — e.g., "請求書" → grep filenames; "先月" → filter by mtime within the previous calendar month.
3. **Re-rank semantically.** Apply your own judgment over the candidate list using the query intent, extension, surrounding context, and naming clues.
4. **Present the top 5 with reasons.** Format each line as:

   ```
   <icon> <name>  <size> · <date>  — <why this matched>
   ```

   Reasons matter more than rank — if the user is going to override your top choice, they should see why.

## Workflow — Duplicates

1. Run `scripts/find_duplicates.py <target>`. Output contains `hash_groups` (identical content) and `name_groups` (suspicious name patterns).
2. Show each group as: `<group_id> (N files, ~XX MB wasted):` followed by each file's path + size.
3. For each group, **propose** which to keep using this heuristic in order: (a) shortest, cleanest filename (no `(N)`, no `コピー`); (b) oldest mtime when content is identical; (c) most structured path (already inside a meaningful folder). The rest move to `_tidy_review/duplicates/<group_id>/`.
4. **Never auto-delete duplicates.** The user reviews `_tidy_review/` themselves.

## When to invoke

**Strong triggers** (definitely use this skill):

- "デスクトップを整理して" / "clean up my Downloads"
- "重複ファイルを探して" / "find duplicates" / "同じファイルが何個もある"
- "先月の請求書どこ？" / "where's that pitch deck"
- "未整理のファイルが多すぎる" / "I have 437 files on my desktop"
- "ファイル整理を手伝って" / "help me organize"

**Don't use this skill for:**

- Code-refactoring tasks or organizing source files inside a project — use grep / language tools instead.
- Cloud storage (Google Drive, Dropbox, iCloud). This skill operates on the local filesystem only.
- Deleting files. Even when the user asks. Move to `_tidy_review/` and let them empty it themselves.

## Output style

Lead with the proposed plan as a compact tree, then ask. Don't narrate every internal step — the user wants to see what's going to happen and decide. Use Japanese or English to match the user's input language.

A good organize-plan output looks like:

```
~/Desktop (24 files, 2 likely duplicates)

Photos/2026-04/        (5)
Screenshots/2026-04/   (2)
Screenshots/2026-05/   (1)
Invoices/              (4)   ← 請求書/領収書 を含むPDF
Documents/卒論/         (3)
Video/                 (1)
Design/                (1)
_tidy_review/
  duplicates/g01/      (2)   ← 請求書_4月分.pdf と 請求書のコピー.pdf
  duplicates/g02/      (2)   ← 卒論_第3章_v7.docx の重複
  unknown/             (3)   ← Untitled.docx 等、自動判別を避けたもの

適用していい？(yes / 修正したい点があれば教えてください)
```

## Reference files

- `references/categorization-rubric.md` — how to choose categories and date sub-buckets

## Reverting a move

If the user wants to undo, read the most recent journal: `cat <target>/.tidy-journal.jsonl | tail -n N`. Each line is `{"from": ..., "to": ...}`. Reverse the moves in the reverse order they were applied. Surface anything that has been further edited since the move and let the user decide.
