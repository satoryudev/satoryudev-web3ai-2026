# Lecture 6 — プロトタイプ v5

VPC v1 で構想した **Tidy（AIファイル整理アシスタント）** の「動くプロトタイプ v5」。
第8回のインタビュー結果を v4 で1件、v5 でもう1件、本体に反映する回。

## 進化マップ

| | テーマ | 何で答えたか |
|---|---|---|
| v1 | 見栄え（mock） | 静的 HTML デモ |
| v2 | 信頼性 — 怖くないから押せる | 削除しない・見せてから動く・全部戻せる |
| v3 | 関係性 — コードを壊さない | import / 参照を解析、連結クラスタを一緒に運ぶ |
| v4 | 実用性 — 普通の使い方が普通に動く | `~/Downloads → ~/Documents` 振り分けバグを本体修正（cross-target） |
| **v5** | **継続性 — 安全に貯めたものを自分で完結できる** | **`review` で `_捨て/` を一覧 / 復元 / 物理削除。preview にサマリ行を追加** |

## 成果物

| 形態 | 場所 | 用途 |
|---|---|---|
| 🌐 Web プロトタイプ v5 | https://tidy-prototype-v5.vercel.app | 価値を伝えるデモ（Discord 提出用） |
| 🤖 実装（本物） | https://github.com/satoryudev/tidy | 実際にファイル整理を行う Claude Code Skill（テスト **105 項目** 合格） |
| 📄 ソースコード | [`prototype/index.html`](./prototype/index.html) | Web プロトタイプ v5 のコード |
| 🌐 v4 / v3 / v2 / v1 | tidy-prototype-{v4,v3,v2,v1}.vercel.app | 比較用に残置 |

## 第8回インタビューから得た気づき（一言）

> **継続利用の決め手は「派手な新機能」ではなく「自分の普段のフローが普通に動くか / 安全に貯めたものを自分で片付けられるか」**

最初に出た声「Downloads を別 dir に振り分けたい」を v4 で対応。
それを使ってもらった次に出てきた声「_捨て にどんどん溜まる気がする、後で見返したり片付けたりするフローが欲しい」を v5 で対応。

## v4 → v5 で変えたこと（1〜2個）

### 1. `review` サブコマンド — `_捨て/` の lifecycle 管理

`_捨て/` は v2 から「削除しない代わりに隔離する場所」として作っていたが、**溜まり続けることへのケアが無かった**。`review` でそれを完結させる:

```bash
# 一覧（隔離日時・元の場所・理由を manifest から引いて表示）
tidy review ~/Documents

# パターンで復元（apply と同じ衝突回避）
tidy review ~/Documents --restore "*.pdf" --yes

# 古いものを物理削除（tidy 唯一の delete 経路、不可逆、必ず --yes 必須）
tidy review ~/Documents --purge --older-than 30 --yes
```

`--restore` も `--purge` も `--yes` ゲート付き。`--purge` は dry-run のとき
件数と合計サイズだけ出して停止する。

### 2. preview のサマリ行

```
== 整理プレビュー（dry-run・移動しません） ==
対象: ~/Documents
移動予定: 24 件 / 総サイズ 187.3 MB (うち _捨て/ へ 4.2 MB)

サマリ: _捨て/ 5件 / コード/ 4件 / ドキュメント/ 12件 / 画像/ 3件   ← v5 追加
```

100件規模の plan でも「どこに何件行くか」を1行で把握できるように。

実装: [`satoryudev/tidy@3a71b8f`](https://github.com/satoryudev/tidy/commit/3a71b8f) — テスト 89 → 105（+16）

## 次のステップ（最終発表 7/16 に向けて）

- 「インストール → Downloads 整理 → review → 古いものは purge」までの **一気通貫ライブデモ**を最終発表で見せる
- ドキュメント整備（SKILL.md / classification.md を初めての人が読んでも分かる粒度に）
- 別の人にも 1〜2 人試してもらって、`review` の体験で次の声を拾う

## ローカルで動かす

```bash
# Web プロトタイプ v5
open lectures/lecture6/prototype/index.html

# 実装（本物）をインストールして使う
git clone https://github.com/satoryudev/tidy.git
ln -s "$(pwd)/tidy" ~/.claude/skills/tidy
# 例:
#   「Downloads の中身を Documents の下に振り分けて」
#   「_捨て の中身見せて、30日より古いやつは消していい」
```

---

## Discord 投稿ドラフト（5項目・本人が投稿する）

```
【プロジェクト名】Tidy — AIファイル整理アシスタント（Claude Code skill）

【URL】https://tidy-prototype-v5.vercel.app

【第8回インタビューでの一番大きな気づき】
継続利用の決め手は「派手な新機能」ではなく「自分の普段のフローが普通に動くか」。最初に出た「Downloads を別 dir に振り分けたい」を v4 で本体修正したら、次は「_捨て にどんどん溜まる、後で見返したり片付けたりするフローが欲しい」が出た。

【v4 → v5 で変えたこと】
1. `review` サブコマンド追加 — `_捨て/` の中身を一覧（隔離日時・元の場所・理由）、`--restore "*.pdf" --yes` で元の場所に復元、`--purge --older-than 30 --yes` で古いものだけ物理削除（tidy 唯一の delete 経路、必ず --yes ゲート）。「削除しない」の次の世代「安全に貯めたものを自分で完結できる」を実装。
2. preview のサマリ行 — 「どこに何件行くか」を1行で把握できるよう、移動予定行の直下に「サマリ: コード/ 4件 / ドキュメント/ 12件 / _捨て/ 5件」を追加。
（テスト 89 → 105 項目 / 実装: satoryudev/tidy@3a71b8f）

【次のステップ（7/16 最終発表に向けて）】
・「インストール → Downloads 整理 → review → 古いものは purge」までを一気通貫ライブデモで見せる
・SKILL.md / classification.md を初見でも読める粒度にドキュメント整備
・別の人にも試してもらって `review` の体験で次の声を拾う
```
