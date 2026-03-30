# コンテンツ部署

## 役割
JapanSaunaのHPコラム記事の企画・執筆・品質管理・公開管理を担当する。
SEO・リード獲得・ブランディングを目的としたコラム記事をガンガン量産する。

## SEO担当範囲（記事単位の実行）
- marketingが選定したキーワードを記事に適切に組み込む
- タイトル・見出し（H2/H3）・メタディスクリプションのSEO最適化
- 内部リンクの設置（関連記事・LP・問い合わせページへの誘導）
- QCチェック項目にSEOキーワードの適切な使用を含める

## ターゲット読者
- BtoC：新築戸建住宅を建てる30代男性
- BtoB：ホテル・ヴィラ・民泊へのサウナ導入検討者

## ロール

### Writer（執筆担当）
- ネタ帳（topics/）からテーマを選んで記事を執筆する
- 執筆中の記事は `drafts/` に保存する
- ファイル名：`YYYY-MM-DD-kebab-title.md`
- 記事フォーマット（下記参照）に従って書く

### QC（品質管理）
- `drafts/` の記事をレビューし、`review/` に品質チェック結果を保存する
- チェック観点：SEOキーワード・読みやすさ・CTA・ターゲット一致・事実確認
- OKなら `published/` に移動し、公開日・URLを記録する
- NGなら差し戻しコメントを付けて Writer に戻す

## 記事フォーマット

```markdown
---
title: 記事タイトル
target: BtoC / BtoB / 両方
keyword: メインキーワード
status: draft / review / published
created: YYYY-MM-DD
published_date: YYYY-MM-DD（公開後に記入）
url: （公開後に記入）
---

## 導入
（読者の悩み・興味を引く書き出し）

## 本文
（H2・H3で構成、1500〜3000字目安）

## まとめ
（要点整理 ＋ CTAへの誘導）

## CTA
（問い合わせ・資料請求・モデルハウス見学など）
```

## ワークフロー

```
topics/（ネタ帳）
  ↓ Writer が執筆
drafts/（執筆中・完成稿）
  ↓ QC がレビュー
review/（チェック記録）
  ↓ OK
published/（公開済み管理）
```

## フォルダ構成
- `topics/` - 記事ネタ帳・キーワードリスト
- `drafts/` - 執筆中・完成稿（QCに回す前）
- `review/` - QCチェック記録・差し戻しコメント
- `published/` - 公開済み記事・URL・公開日管理

## 運営ルール
- 同日ファイルは追記（新規作成しない）
- ネタは `topics/idea-list.md` に随時追記
- 公開済みは `published/published-log.md` に一覧管理
