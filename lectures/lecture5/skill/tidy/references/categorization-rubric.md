# Categorization Rubric

Use this rubric when proposing a category tree for a directory. The goal is *"the user can find anything in 3 seconds"* while keeping the folder count low — too many categories is its own kind of mess.

## Default top-level categories

Pick from this list. Don't invent novel categories unless more than 3 files clearly demand it.

| Category          | Goes here                                                    |
|-------------------|--------------------------------------------------------------|
| `Photos/`         | `.jpg .jpeg .png .heic .raw .webp` from cameras (`IMG_*`, `DSC_*`, phone exports) |
| `Screenshots/`    | Anything matching `Screenshot*`, `Screen Shot*`, `スクリーンショット*` |
| `Documents/`      | `.pdf .docx .doc .pages .txt .md` general-purpose            |
| `Invoices/`       | PDFs whose name contains 請求書 / 領収書 / Invoice / Receipt / Bill |
| `Spreadsheets/`   | `.xlsx .csv .numbers .ods`                                   |
| `Slides/`         | `.pptx .key .odp`                                            |
| `Design/`         | `.fig .sketch .psd .ai .xd`                                  |
| `Code/`           | Lone source files (`.py .ts .rs ...`), repo archives         |
| `Video/`          | `.mp4 .mov .mkv .webm`                                       |
| `Audio/`          | `.mp3 .wav .flac .m4a .aac`                                  |
| `Archives/`       | `.zip .tar.gz .7z` that aren't code                          |
| `_tidy_review/`   | Anything ambiguous. Always prefer this over `Misc/`          |

## Date sub-buckets

For categories where date matters (`Photos/`, `Screenshots/`, `Invoices/`), sub-bucket by `YYYY-MM/` based on **mtime**, not name parsing — mtime is more reliable across locales and apps.

Skip date sub-buckets when the category has fewer than ~6 files, otherwise you end up with many near-empty folders.

## Decision principles

1. **Extension first, name patterns second.** `.pdf` alone doesn't tell you it's an invoice; the name `請求書_4月.pdf` does. Use both signals together.
2. **No empty folders.** If only 2 invoices exist, don't create `Invoices/2026-01/` and `Invoices/2026-04/`. Put both directly under `Invoices/`.
3. **Ambiguous → `_tidy_review/`.** Better to leave a file for the user to glance at than to mis-file it. Trust degrades fast when the wrong file ends up in the wrong bucket.
4. **Preserve compound naming as a clustering hint.** A file named `卒論_第3章_v7.docx` belongs in `Documents/卒論/` if there are multiple 卒論 files. Use shared prefixes as a clustering signal.
5. **Don't rename files.** Tidy moves, doesn't rename. Renaming breaks references the user has elsewhere (links, scripts, muscle memory).

## Bad patterns to avoid

- ❌ `Misc/` as a dumping ground — use `_tidy_review/` instead so the user knows it needs attention.
- ❌ Deep hierarchies (more than 2 levels) for v1.
- ❌ Splitting by year *and* month when 4 files exist. Pick the granularity the file count justifies.
- ❌ Categories the user didn't ask for that "feel useful" (`Important/`, `ToReview/`). The user defines what's important — don't impose.

## Sample plan (24 files on Desktop)

```
~/Desktop/
├── Photos/
│   └── 2026-04/   (5 files)
├── Screenshots/
│   ├── 2026-04/   (2 files)
│   └── 2026-05/   (1 file)
├── Invoices/      (4 files)
├── Documents/
│   └── 卒論/       (3 files)
├── Video/         (1 file)
├── Design/        (1 file)
└── _tidy_review/
    ├── duplicates/
    │   ├── g01/   (2 files — 請求書 重複)
    │   └── g02/   (2 files — 卒論 v7 重複)
    └── unknown/   (3 files — Untitled.docx 等)
```

24 files → 6 real categories + 1 review area. That's a reasonable v1 outcome.
