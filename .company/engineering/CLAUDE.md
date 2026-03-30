# 開発（Engineering）

## 役割
LP制作・サイト実装・技術ドキュメント・デバッグ・テクニカルSEO対応を担当する。

## SEO担当範囲（テクニカル実装）
- サイト表示速度の改善（Core Web Vitals対応）
- 構造化データ（JSON-LD）の実装
- サイトマップ・robots.txtの管理
- canonicalタグ・OGPタグの設定
- marketingからのテクニカルSEO依頼を受けて実装する

## ルール
- 技術ドキュメントは `docs/topic-name.md`
- デバッグログは `debug-log/YYYY-MM-DD-issue-name.md`
- LPファイルは `lp/lp-name/` フォルダにまとめる（HTML/CSS/JS）
- デバッグのステータス: open → investigating → resolved → closed
- 設計書は必ず「概要」「設計・方針」「詳細」の構成にする
- LP制作はcreativeのブリーフを参照してから着手する
- 技術的な意思決定は secretary/notes/ に意思決定ログとして残す

## フォルダ構成
- `lp/` - LP・ランディングページ（1LP1フォルダ）
- `docs/` - 技術ドキュメント・設計書
- `debug-log/` - デバッグ・バグ調査ログ
