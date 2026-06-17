# Lecture 6 — プロトタイプ v4

VPC v1 で構想した **Tidy（AIファイル整理アシスタント）** の「動くプロトタイプ v4」。
価値検証回 — **v3 を実際に人に見せて、フィードバックを受け、その場で本体を直して v4 として返した**。

## 進化マップ

| | テーマ | 何で答えたか |
|---|---|---|
| v1 | 見栄え（mock） | 静的 HTML デモ |
| v2 | 信頼性 — 怖くないから押せる | 削除しない・見せてから動く・全部戻せる |
| v3 | 関係性 — コードを壊さない | import / 参照を解析、連結クラスタを一緒に運ぶ |
| **v4** | **実用性 — 普通の使い方が普通に動く** | **ユーザに見せたら出た「Downloads を別フォルダへ振り分けたい」を本体で対応** |

## 成果物

| 形態 | 場所 | 用途 |
|---|---|---|
| 🌐 Web プロトタイプ v4 | https://tidy-prototype-v4.vercel.app | 価値を伝えるデモ（Discord 提出用） |
| 🤖 実装（本物） | https://github.com/satoryudev/tidy | 実際にファイル整理を行う Claude Code Skill（テスト **89 項目** 合格） |
| 📄 ソースコード | [`prototype/index.html`](./prototype/index.html) | Web プロトタイプ v4 のコード |
| 🌐 v3 / v2 / v1 | tidy-prototype-{v3,v2,v1}.vercel.app | 比較用に残置 |

## 価値検証で起きたこと（ステップ1〜3）

v3 を人に見せて「継続して使いたい？」を聞いた。返ってきた質問:

> 「Downloads のデータをホームディレクトリの別のディレクトリに移動とかできないの？」

これが**普通の人の最初の自然な要求**だった。
試したら、当時の v3 は **対応していなかった**: `--target` に別 dir を指定して `apply` するとエラーで落ちる。
plan の `from` が「scan 元への相対パス」のまま出ていて、`apply` が「target からの相対」と解釈してファイルを見つけられない、というバグだった。

**「コードを壊さない」を v3 で謳ったその次の瞬間に、「普通のユースケース」を壊していた**ことが分かった。価値検証の意味そのもの。

## v4 で実装したこと（v3 → v4 差分）

| 観点 | v3 | v4 |
|---|---|---|
| Downloads → ホーム配下への振り分け | バグで動かない（実用上は使えない） | **`scan ~/Downloads / suggest --target ~/Documents` で素直に動く** |
| 単一 root + 別 target の判定 | `multi_root` 限定で判定していた | **`cross_target = multi_root OR (target ≠ scan root)` に一般化** |
| from 値 | 単一 root のとき強制で相対パス | **cross_target なら絶対パス**（実ファイルの場所を指す） |
| target 配下スキップ | multi_root だけで実行 | **cross_target で常時実行**（target 内のファイルは「移動不要」として skipped へ） |
| テスト | 82 項目 | **89 項目**（+7・cross-target 単一ソースのフルラウンドトリップ） |

実装: [`satoryudev/tidy@0eb3c5e`](https://github.com/satoryudev/tidy/commit/0eb3c5e)

一言でいうと: **「機能を作る」より「フィードバックを聞いて直す」が価値検証の本体**。
v3 ではエラーで止まっていた「Downloads の中身をホーム配下のどこかに振り分ける」が、v4 では普通に動く。

## ローカルで動かす

```bash
# Web プロトタイプ v4
open lectures/lecture6/prototype/index.html

# 実装（本物）をインストールして使う
git clone https://github.com/satoryudev/tidy.git
ln -s "$(pwd)/tidy" ~/.claude/skills/tidy
# あとは Claude Code に：
#   「Downloads の中身を Documents の下に振り分けて」
#   「~/Downloads 整理して、ホーム配下に振り分けて」
# などと頼むだけ
```

---

## Discord 投稿ドラフト（ステップ4・本人が投稿する）

```
第9回課題（プロダクト v4 価値検証）

【v3 → v4 差分】
・ユーザに「Downloads の中身をホームディレクトリの別ディレクトリに振り分けたい」と聞かれた → v3 では apply がバグで動かなかった部分を本体で修正
・suggest の cross_target 判定を multi_root だけでなく「単一 root でも target が異なる場合」に拡張
・plan の from を絶対パスで出力するロジックを統一（target 配下のファイルは skipped へ）
・新規テスト t_suggest_cross_target_single_source（〜/Downloads 想定 → 別 target dir → apply → undo の完全ラウンドトリップ）追加
・テスト 82 → 89 項目（+7）

【継続して使いたいか？に対するフィードバック】
「Downloads の中身をホームディレクトリの別ディレクトリに移動とかできないの？」── 実際に試してもらったらこれだった。継続利用に必要だったのは「派手な新機能」ではなく「自分の普段のフローに合うか」。v3 はそこを満たせていなかった。

【得た気づき】
価値検証は「便利か？」じゃなく「あなたの状況で実際に動くか？」を見るのが本質だと分かった。自分が考えた使い方（その場整理 / 集約モード）の外側に、ユーザの「普通の使い方」があった。コードを書く前に「使ってもらう」を1回入れるだけで、優先順位がガラッと変わる。

【URL】
https://tidy-prototype-v4.vercel.app/
```
