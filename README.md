# AIエージェント（Aimee）プロジェクト ドキュメント構成

## 📁 ディレクトリ構成

```
new_trance_cosmos/
├── README.md                    # このファイル
├── 01_requirements/             # 要件定義
│   └── requirements.md          # システム要件定義書
├── 02_database/                 # データベース関連
│   ├── design/                  # DB設計
│   │   ├── 01_overview.md       # DB設計概要
│   │   └── 02_table_specifications.md  # テーブル仕様詳細
│   ├── diagrams/                # ER図
│   │   └── 01_er_diagram.md     # ER図（ビジュアル表現）
│   └── scripts/                 # SQLスクリプト
│       └── init.sql             # DB初期化スクリプト
├── 03_data/                     # データ要件
│   └── data_requirements.md     # 必要データ一覧と取得方法
├── 04_architecture/             # システム構成（今後作成）
├── 05_ui/                       # UI設計（今後作成）
├── backend/                     # バックエンド実装
├── frontend/                    # フロントエンド実装
├── config/                      # 設定ファイル
└── data/                        # サンプルデータ
```

## 📋 ドキュメント一覧

### 1️⃣ 要件定義 (`01_requirements/`)
- **requirements.md**: システム全体の要件定義書
  - プロジェクト概要
  - 機能要件・非機能要件
  - UI画面構成（6画面）
  - 技術スタック

### 2️⃣ データベース設計 (`02_database/`)
#### design/
- **01_overview.md**: DB設計の概要説明
  - テーブル構成（全20テーブル）
  - インデックス戦略
  - データ保持ポリシー
  
- **02_table_specifications.md**: 各テーブルの詳細仕様
  - 全カラムの説明
  - データ型・制約
  - インデックス一覧

#### diagrams/
- **01_er_diagram.md**: ER図（視覚的表現）
  - ASCII アートでのテーブル関係図
  - データフロー図
  - テーブル利用マトリクス

#### scripts/
- **init.sql**: データベース初期化スクリプト
  - CREATE TABLE文
  - 初期データ投入
  - ビュー・ストアドプロシージャ

### 3️⃣ データ要件 (`03_data/`)
- **data_requirements.md**: 必要データと取得方法
  - 現在受取済みデータ（CSV/Excel）
  - 今後必要なデータ
  - データ更新頻度・保持期間

### 4️⃣ アーキテクチャ設計 (`04_architecture/`) ※今後作成
- システム構成図
- コンポーネント設計
- API仕様

### 5️⃣ UI設計 (`05_ui/`) ※今後作成
- 画面遷移図
- ワイヤーフレーム
- UIコンポーネント仕様

## 🚀 クイックスタート

1. **要件確認**: `01_requirements/requirements.md` を読む
2. **DB構築**: `02_database/scripts/init.sql` を実行
3. **データ準備**: `03_data/data_requirements.md` を確認

## 📝 議事録からの主要決定事項

### 2025年8月22日
- UI開発方針: Streamlitで6画面構成
- 情報量を削ぎ落とし、使いやすくブラッシュアップ

### 2025年8月8日  
- バッチ2: 数値化できるデータ（配置情報）
- バッチ3: 数値化しづらいデータ（実績・ノウハウ）
- 個人別配置データは要開発

### 2025年8月1日
- 拠点間最適化はモード選択可能に
- 出勤情報は不要と決定
- RAG更新は週次で問題なし

## 🔗 関連リンク

- [システム構成図](https://app.diagrams.net/?splash=0#G1kBIJvslm_yRlK2QyCbrDwr9GZnJFTb3X#%7B%22pageId%22%3A%22e9641724-42f0-e67c-9413-5a0d33d9c1b3%22%7D)
- [全体概要（Notion）](https://pouncing-attic-dd0.notion.site/24154d8b9bc0807c8dfbc7278e5655cf)