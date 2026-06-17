# Lecture 6 — プロトタイプ v3

VPC v1 で構想した **Tidy（AIファイル整理アシスタント）** の「動くプロトタイプ v3」。
v1 の「見た目だけの mock」→ v2 の「**怖くないから押せる**（消さない・戻せる・見せる）」を経て、
v3 で **コードファイルを扱えるようになった**。

## 成果物

| 形態 | 場所 | 用途 |
|---|---|---|
| 🌐 Web プロトタイプ v3 | https://tidy-prototype-v3.vercel.app | 価値を伝えるデモ（Discord 提出用） |
| 🤖 実装（本物） | https://github.com/satoryudev/tidy | 実際にファイル整理を行う Claude Code Skill（テスト **82 項目** 合格） |
| 📄 ソースコード | [`prototype/index.html`](./prototype/index.html) | Web プロトタイプ v3 のコード |
| 🌐 v2（比較用） | https://tidy-prototype-v2.vercel.app | 第6回 v2 のデモ |
| 🌐 v1（比較用） | https://tidy-prototype-v1.vercel.app | 第5回の mock デモ |

## v2 を使ってみて気づいた違和感（ステップ1）

- v2 は「怖くないから押せる」が完成して、実際に Desktop を整理してみた。安心して動かせた。
- ところが**コードが入ったフォルダ**に当てると問題が出た: `main.py` と `helper.py` が
  別の subfolder に振り分けられて、`from helper import x` の **import が壊れた**。
- 整理した結果ファイルは生きているのに、**プログラムが動かなくなる**。
  → 「壊さない」の盲点だった。**消さなくても、関係性が切れたら壊れる**。
- 関連して: 1ファイルずつ plan を手書きするのも辛い。`scan.json` 200行から `plan.json` を
  作るのに時間がかかる。**baseline を自動生成してほしい**。

## v3 で実装したこと（v2 → v3 差分）

| 観点 | v2 | v3（新規） |
|---|---|---|
| コードの扱い | 1ファイルずつ分類 | **依存解析（import/require/src=/href=/@import）→ 連結クラスタを同じ subfolder にまとめて運ぶ** |
| クラスタ分断防止 | なし | **preview がクラスタ分断/未カバーを検出して警告**（import が壊れる前に止める） |
| plan の作成 | 手書き or 試行錯誤 | **`suggest` が scan.json から baseline plan を自動生成**。人は差分修正だけ |
| 整合性 | 自分で確認 | **`verify` で apply 直後に from が消え/to が存在を機械チェック** |
| やり直し | undo のみ | **`redo` を追加**（undo を取り消して apply 後の状態へ） |
| 中断 | OSError で停止 | **Ctrl-C を捕まえて安全終了**（journal をフラッシュ・rc=130）→ そのまま undo 可 |
| プレビュー | 件数のみ | **総サイズ + `_捨て/` への隔離サイズ** を表示 |
| 自己移動 | apply 時にエラー | **preview で from==to を早期検出** |
| テスト | 35 項目 | **82 項目**（+47） |

一言でいうと: **「怖くないから押せる」→「コードでも壊さず動ける」**。
依存関係を見て関連ファイルを一緒に運ぶ。`scan` → `suggest`（自動 baseline）→ `preview` → `apply` → `verify`。
途中の Ctrl-C も安全。

## 対応する依存元（v3）

- **Python**: `from X import Y`（dot relative + sibling 慣習）/ `import X`
- **JS/TS/JSX/TSX/MJS/CJS**: `import ... from './X'` / `require('./X')` / 動的 `import('./X')` / 拡張子補完 / `/index.{js,ts,...}`
- **HTML**: `src=` / `href=` のローカル参照（外部 URL は除外）
- **CSS/SCSS/SASS**: `@import` / `url(...)`
- **Markdown**: `![alt](./img.png)` のローカル参照
- **Shell**: `source ./other.sh` / `. ./other.sh`

外部パッケージ（`react`, `os`, `requests`）は解決不能で自然に除外されるため、誤検出はほぼ無い。

## ローカルで動かす

```bash
# Web プロトタイプ v3
open lectures/lecture6/prototype/index.html

# 実装（本物）をインストールして使う
git clone https://github.com/satoryudev/tidy.git
ln -s "$(pwd)/tidy" ~/.claude/skills/tidy
# あとは Claude Code に「このフォルダを整理して」「講義資料をまとめて」と頼む
```

---

## Discord 投稿ドラフト（ステップ5・本人が投稿する）

> ⚠️ ステップ3〜5（**1人以上に見せる → 感想・気付きを記録 → 自分の言葉で投稿**）は
> 自分自身で行う必要があります。下書きの「見せて得た気付き」は実際に見せてから埋めてください。

```
【プロトタイプ v3 / Tidy】

一言ピッチ：v2 は「怖くないから押せる」を作った。v3 は「コードを壊さない」を入れた — import を読むようになり、main.py と helper.py を一緒に運ぶ。82テスト合格。

デプロイURL：https://tidy-prototype-v3.vercel.app
実装（本物）：https://github.com/satoryudev/tidy

v2 → v3 の差分：依存解析（py/js/html/css/md）→ 連結クラスタを同じ subfolder にまとめる／suggest で baseline plan 自動生成／verify で整合性チェック／redo で undo の取り消し／Ctrl-C で安全終了。

見せて得た自分の感想・気付き：（★ここに記入★ — 例：「コードフォルダでも壊れないと分かった瞬間に “普段触れない場所” に手を入れる気になった」「自動 plan があると“まず動かす”心理障壁が下がる」など）

他の受講生への問い：あなたが「自動化したいけど“関係性が切れる”のが怖くて手を出せない」場所はどこですか？
```
