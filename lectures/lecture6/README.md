# Lecture 6 — プロトタイプ v6

VPC v1 で構想した **Tidy（AIファイル整理アシスタント）** の「動くプロトタイプ v6」。
v5 で「1つの場所の捨て箱を片付けられる」を作ったあと、
「**どこを・いつ整理したかを1か所で振り返りたい**」という声に v6 で答えた。

## 進化マップ

| | テーマ | 何で答えたか |
|---|---|---|
| v1 | 見栄え（mock） | 静的 HTML デモ |
| v2 | 信頼性 — 怖くないから押せる | 削除しない・見せてから動く・全部戻せる |
| v3 | 関係性 — コードを壊さない | import / 参照を解析、連結クラスタを一緒に運ぶ |
| v4 | 実用性 — 普通の使い方が普通に動く | `~/Downloads → ~/Documents` 振り分けバグを本体修正（cross-target） |
| v5 | 継続性 — 安全に貯めたものを自分で完結できる | `review` で `_捨て/` を一覧 / 復元 / 物理削除。preview にサマリ行 |
| **v6** | **一望性 — どこを・いつ整理したかを1本で辿れる** | **`history` で全ての場所の操作を `~/.tidy` に集約し、横断タイムライン表示** |

## 成果物

| 形態 | 場所 | 用途 |
|---|---|---|
| 🌐 Web プロトタイプ v6 | https://tidy-prototype-v6.vercel.app | 価値を伝えるデモ（Discord 提出用） |
| 🤖 実装（本物） | https://github.com/satoryudev/tidy | 実際にファイル整理を行う Claude Code Skill（テスト **114 項目** 合格） |
| 📄 ソースコード | [`prototype/index.html`](./prototype/index.html) | Web プロトタイプ v6 のコード |
| 🌐 v5 / v4 / v3 / v2 / v1 | tidy-prototype-{v5,v4,v3,v2,v1}.vercel.app | 比較用に残置 |

## v6 で答えた声（一言）

> **「複数の場所を整理していくと、どこを・いつ・何を動かしたか分からなくなる。1か所で振り返れないの？」**

v5 までは各ディレクトリの `_整理ログ/manifest-*.json` に記録は残っていたが、**場所ごとに分散**していて横串で見られなかった。「先週 tidy で何やったっけ」に答えられない。

## v5 → v6 で変えたこと（1個）

### `history` サブコマンド — 全ての場所の操作を1本のタイムラインで

apply / undo / redo / review-restore / review-purge が成功するたび、その1行が
`~/.tidy/history.jsonl` に集約される。どのフォルダを整理しても履歴は1本に集まる。

```bash
# 全ての場所の操作を新しい順に（いつ・何を・どこで）
tidy history

# 特定ディレクトリの操作だけに絞る
tidy history --target ~/Documents

# manifest / ログのパスも表示
tidy history --verbose
```

表示例:
```
== tidy 操作履歴 ==
記録数: 4 件（最新 4 件を表示）

  2026-06-24 17:24  ✕ 物理削除  12 件を物理削除（4.2 MB）
      場所: /Users/you/Documents
  2026-06-24 17:20  ▸ 整理  24 件移動（うち 5 件を隔離）
      場所: /Users/you/Documents
  2026-06-23 09:10  ▸ 整理  8 件移動（うち 2 件を隔離）
      場所: /Users/you/Downloads
  2026-06-22 21:03  ↩ 取り消し  8 件を復元
      場所: /Users/you/Downloads
```

**設計のキモ**: 「散らかりの整理」自体は従来どおりローカル（同一ボリューム内の rename）で行い、
ホームに置くのは **来歴の索引だけ**。実ファイルは動かさないので、外付けドライブでも速度・安全性は
変わらない。環境変数 `TIDY_HOME` で保存先を差し替えられる（テストや複数環境用）。

実装: [`satoryudev/tidy@55bb104`](https://github.com/satoryudev/tidy/commit/55bb104) — テスト 105 → 114（+9）

## 次のステップ（最終発表 7/16 に向けて）

- `history` を土台に、Obsidian vault へ整理履歴をエクスポートする導線（履歴の索引ができたので上に載せられる）
- 「インストール → Downloads 整理 → review → history で振り返り」までの一気通貫ライブデモ
- 別の人にも試してもらい、`history` の体験で次の声を拾う

## ローカルで動かす

```bash
# Web プロトタイプ v6
open lectures/lecture6/prototype/index.html

# 実装（本物）をインストールして使う
git clone https://github.com/satoryudev/tidy.git
ln -s "$(pwd)/tidy" ~/.claude/skills/tidy
# 例:
#   「Downloads の中身を Documents の下に振り分けて」
#   「先週 tidy で何やったか見せて」  ← v6
```

---

## Discord 投稿ドラフト（5項目・本人が投稿する）

```
【プロジェクト名】Tidy — AIファイル整理アシスタント（Claude Code skill）

【URL】https://tidy-prototype-v6.vercel.app

【第8回インタビューでの一番大きな気づき】
継続利用の決め手は「派手な新機能」ではなく「自分の普段のフローが普通に動くか / 後から自分で辿れて片付けられるか」。使ってもらうほど、機能そのものより「安心して任せ続けられる土台」への要望が出てくる。

【v5 → v6 で変えたこと】
`history` サブコマンドを追加。apply / undo / redo / review の操作が、どのフォルダを整理しても ~/.tidy/history.jsonl に1本のタイムラインで集約される。「先週どこを・いつ・何を整理したっけ」を横断で振り返れる。--target で場所を絞れる。実ファイルは動かさず来歴の索引だけをホームに置く設計なので、速度・安全性はそのまま。テスト 105 → 114 項目。

【次のステップ（7/16 最終発表に向けて）】
・history を土台に Obsidian への履歴エクスポート導線
・「インストール → 整理 → 片付け → 振り返り」を一気通貫ライブデモ
・別の人にも試してもらって次の声を拾う
```
