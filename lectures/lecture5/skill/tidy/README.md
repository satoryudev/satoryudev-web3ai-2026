# Tidy Skill — Claude Code 用

Tidy プロトタイプ v1 のコンセプトを Claude Code (および互換の AI エージェント) で動かせる **skill** にしたものです。エージェントに「あなたの散らかったフォルダを片付ける役割」をインストールします。

## できること

- **Organize** — `~/Desktop` などのディレクトリをスキャンして、カテゴリツリーへ自動振り分け (ドライラン → 承認 → 適用)
- **Search** — 「先月の請求書」「卒論のPDF」などの自然言語クエリで該当ファイル探索
- **Duplicates** — 内容ハッシュ + 名前パターン (`のコピー`, `(3)`) で重複検出。削除はせず `_tidy_review/` に隔離

## セキュリティ

- 必ず **ドライラン → 承認** のフロー
- **削除はしない**。重複や判別不能なファイルは `_tidy_review/` に移動するのみ
- すべての移動を `.tidy-journal.jsonl` に記録するので、間違えても巻き戻し可能

## インストール

### Claude Code (ローカル)

```bash
# 個人スキルとして
mkdir -p ~/.claude/skills
cp -r lectures/lecture5/skill/tidy ~/.claude/skills/

# またはリポジトリ単位のスキルとして
mkdir -p .claude/skills
cp -r lectures/lecture5/skill/tidy .claude/skills/
```

Claude Code を再起動すると、`Skill(tidy)` または該当する自然言語プロンプトでトリガーされます。

### 動作要件

- Python 3.9+ (`scripts/` 内のスクリプトを実行するため)
- 標準ライブラリのみ使用、追加 pip パッケージ不要

## ファイル構成

```
tidy/
├── SKILL.md                          # エージェントへの指示書 (フロントマター + 本文)
├── README.md                         # ← このファイル
├── scripts/
│   ├── scan_dir.py                   # ディレクトリスキャン → JSON manifest
│   ├── find_duplicates.py            # 重複検出 (hash + name pattern)
│   └── apply_plan.py                 # 移動プラン適用 (ドライラン / journal)
└── references/
    └── categorization-rubric.md      # カテゴリ判定ルール
```

## 試し方 (手動でスクリプトだけ叩く場合)

```bash
# スキャン
python lectures/lecture5/skill/tidy/scripts/scan_dir.py ~/Desktop --max-depth 1 > manifest.json

# 重複検出
python lectures/lecture5/skill/tidy/scripts/find_duplicates.py ~/Desktop > dupes.json

# プラン適用 (ドライラン)
python lectures/lecture5/skill/tidy/scripts/apply_plan.py plan.json
# 本適用
python lectures/lecture5/skill/tidy/scripts/apply_plan.py plan.json --apply
```

## 由来

- 元になったプロダクト: [Tidy プロトタイプ v1](../../prototype/) (web上のデモ)
- VPC v1: [`../../../lecture3/vpc-v1.md`](../../../lecture3/vpc-v1.md)
- バグ #18: PC やスマホ内のファイル整理が進まない

プロトタイプは「価値を伝える静的デモ」、こちらのスキルは「Claude Code 上で実際に動かせる実装」という関係です。
