# Lecture 5 — プロトタイプ v1

VPC v1 で構想したプロダクトの「動くプロトタイプ v1」を AI と一緒に作って公開する課題。

## 成果物

| 形態 | 場所 | 用途 |
|---|---|---|
| 🌐 Web プロトタイプ | https://tidy-prototype-v1.vercel.app | 価値を伝えるデモ (Discord 提出用) |
| 🤖 Claude Code Skill | [`skill/tidy/`](./skill/tidy/) | AI エージェントが実際にファイル整理を行う実装 |
| 📄 ソースコード | [`prototype/index.html`](./prototype/index.html) | Web プロトタイプのコード |

## プロダクト概要

**Tidy** — 「あとで整理しよう」を終わらせる AI ファイル整理アシスタント。

| 項目 | 内容 |
|---|---|
| 解決するバグ | #18 PCやスマホ内のファイル整理が進まない |
| 誰のため | 自分自身 + 同じ症状を抱えた身近な人 |
| VPC由来 | [`../lecture3/vpc-v1.md`](../lecture3/vpc-v1.md) |

## v1 で動くもの

1. **AI 自動分類** — 散らかった24ファイルを8カテゴリに自動振り分け
2. **自然言語検索** — 「先月の請求書」「旅行の写真」のような曖昧クエリで検索
3. **重複検出** — 「コピー」を含む類似ファイルをハイライト

## 技術スタック

- 静的 HTML + Vanilla JS（v1 はバックエンドなし、UI で価値を伝えることに集中）
- Vercel に静的サイトとしてデプロイ

## ローカルで開く

```bash
# Web プロトタイプ
open lectures/lecture5/prototype/index.html

# Claude Code スキルをインストール
mkdir -p ~/.claude/skills && cp -r lectures/lecture5/skill/tidy ~/.claude/skills/
```

詳細は [`skill/tidy/README.md`](./skill/tidy/README.md) を参照。
