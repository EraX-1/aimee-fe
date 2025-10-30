# AIMEE プロジェクト索引

**最終更新**: 2025-10-26
**バージョン**: 2.0.0

このファイルは、AIMEEプロジェクトの全ドキュメントとリソースへの完全な索引です。

---

## ⚠️ プロジェクトルール

### 開発時の重要ルール

1. **ドキュメント管理**: 新しいドキュメントを作らず、既存のマスタードキュメント（9個）を上書きする
2. **データベース管理**: データベースの挿入データを常に正しく保つ（期待値: operators 100件、progress_snapshots 832件）

**詳細**: [CLAUDE.md](CLAUDE.md) の「プロジェクトルール」セクションを参照

---

## 🎯 初めての方へ

### まず読むべきドキュメント（優先順）

1. **[README.md](README.md)** - プロジェクト概要、最新機能、クイックスタート
2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐️ - 全情報を1ページで（DB、モデル、デプロイ、API等）
3. **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - システム全体図（Mermaid）、処理フロー

---

## 📚 ドキュメント構成

### ルートディレクトリ（マスタードキュメント）

#### 📖 概要・リファレンス
- **[README.md](README.md)** - プロジェクトトップページ
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐️⭐️⭐️⭐️ - クイックリファレンス（全情報）
- **[CLAUDE.md](CLAUDE.md)** ⭐️⭐️⭐️ - Claude Code向けプロジェクト詳細

#### 🏗️ システム・技術
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** ⭐️⭐️⭐️ - システム全体図、処理フロー
- **[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)** ⭐️⭐️ - 実装作業ログ（全履歴）

#### 🔧 セットアップ・運用
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** ⭐️⭐️ - ローカル環境セットアップ
- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** ⭐️⭐️ - AWS本番環境デプロイ
- **[DEMO_SCRIPT_FINAL.md](DEMO_SCRIPT_FINAL.md)** ⭐️ - デモ実施手順

---

### documentsフォルダ（詳細資料・アーカイブ）

#### 📁 業務・仕様
- **[documents/BUSINESS_HIERARCHY.md](documents/BUSINESS_HIERARCHY.md)** - 業務階層構造
- **[documents/IMPLEMENTATION_STATUS.md](documents/IMPLEMENTATION_STATUS.md)** - 実装状況まとめ
- **[documents/MOCK_NAME_CONFIRMATION.md](documents/MOCK_NAME_CONFIRMATION.md)** - モック名確認

#### 🎬 デモ・テスト
- **[documents/DEMO_VIDEO_SCRIPT.md](documents/DEMO_VIDEO_SCRIPT.md)** - デモ動画用台本
- **[documents/DEMO_QUESTIONS.md](documents/DEMO_QUESTIONS.md)** - デモ用質問パターン
- **[documents/REAL_DATA_SUCCESS.md](documents/REAL_DATA_SUCCESS.md)** - 実データテスト結果
- **[documents/test_cases_q1_q6.json](documents/test_cases_q1_q6.json)** - テストケース定義

#### 📊 レポート
- **[documents/reports/](documents/reports/)** - バグ報告、新要件分析
  - **[documents/reports/bug_reports/BUG_REPORT.md](documents/reports/bug_reports/BUG_REPORT.md)** - バグ報告書
  - **[documents/reports/requirement_analysis/](documents/reports/requirement_analysis/)** - Q1～Q6の要件分析
  - **[documents/reports/DATA_SOURCE_REPORT.md](documents/reports/DATA_SOURCE_REPORT.md)** - データソースレポート
  - **[documents/reports/LLM_MODEL_UPGRADE_GUIDE.md](documents/reports/LLM_MODEL_UPGRADE_GUIDE.md)** - モデルアップグレードガイド

#### 📂 その他
- **[documents/README.md](documents/README.md)** - documentsフォルダの索引

---

### 要件定義・設計フォルダ

#### 📋 要件定義
- **[01_requirements/requirements.md](01_requirements/requirements.md)** - 要件定義書

#### 🗄️ データベース設計
- **[02_database/README.md](02_database/README.md)** - DB設計の概要
- **[02_database/design/01_overview.md](02_database/design/01_overview.md)** - DB設計概要
- **[02_database/design/02_table_specifications.md](02_database/design/02_table_specifications.md)** - テーブル仕様書
- **[02_database/diagrams/01_er_diagram.md](02_database/diagrams/01_er_diagram.md)** - ER図

#### 📊 データ要件
- **[03_data/data_requirements.md](03_data/data_requirements.md)** - データ要件
- **[03_data/data_update_log.md](03_data/data_update_log.md)** - データ更新ログ

---

## 🚀 実行スクリプト

### デプロイ・起動

#### AWS本番環境
- **[deploy-to-aws.sh](deploy-to-aws.sh)** ⭐️⭐️⭐️ - AWSワンコマンドデプロイ

#### Docker（推奨）
- **[docker-start-all.sh](docker-start-all.sh)** ⭐️⭐️ - 全体起動
- **[docker-start-backend.sh](docker-start-backend.sh)** - バックエンドのみ起動
- **[docker-start-frontend.sh](docker-start-frontend.sh)** - フロントエンドのみ起動
- **[docker-check-status.sh](docker-check-status.sh)** - 状態確認
- **[docker-stop-all.sh](docker-stop-all.sh)** - 全体停止

#### ローカル実行（開発用）
- **[start_all.sh](start_all.sh)** - ローカル全体起動
- **[start_backend.sh](start_backend.sh)** - ローカルバックエンド起動
- **[start_frontend.sh](start_frontend.sh)** - ローカルフロントエンド起動
- **[check_status.sh](check_status.sh)** - ローカル状態確認

### テスト
- **[run_api_test.py](run_api_test.py)** ⭐️ - APIテスト実行（Q1～Q6）
- **[api_test_results.json](api_test_results.json)** - 最新テスト結果

---

## 📂 ディレクトリ構造

```
aimee-fe/
├── 00_INDEX.md                    # このファイル
├── README.md                      # プロジェクト概要
├── QUICK_REFERENCE.md             # クイックリファレンス
├── CLAUDE.md                      # Claude向けマスター
├── SYSTEM_OVERVIEW.md             # システム全体図
├── IMPLEMENTATION_LOG.md          # 実装ログ
├── INSTALLATION_GUIDE.md          # セットアップガイド
├── DEPLOY_GUIDE.md                # デプロイガイド
├── DEMO_SCRIPT_FINAL.md           # デモスクリプト
│
├── deploy-to-aws.sh               # AWSデプロイスクリプト
├── docker-*.sh                    # Docker起動スクリプト群
├── start_*.sh                     # ローカル起動スクリプト群
│
├── run_api_test.py                # APIテスト
├── api_test_results.json          # テスト結果
│
├── docker-compose.yml             # Docker設定
├── Dockerfile                     # Docker設定
├── requirements.txt               # Python依存関係
│
├── 01_requirements/               # 要件定義
├── 02_database/                   # DB設計
├── 03_data/                       # データ要件
│
├── documents/                     # 詳細資料・アーカイブ
│   ├── README.md                  # documents索引
│   ├── BUSINESS_HIERARCHY.md
│   ├── IMPLEMENTATION_STATUS.md
│   ├── DEMO_VIDEO_SCRIPT.md
│   ├── DEMO_QUESTIONS.md
│   ├── REAL_DATA_SUCCESS.md
│   ├── MOCK_NAME_CONFIRMATION.md
│   ├── test_cases_q1_q6.json
│   └── reports/                   # レポート類
│       ├── bug_reports/
│       ├── requirement_analysis/
│       ├── DATA_SOURCE_REPORT.md
│       └── LLM_MODEL_UPGRADE_GUIDE.md
│
└── frontend/                      # Streamlitアプリ
    ├── app.py
    ├── src/
    │   ├── components/
    │   └── utils/
    ├── README.md
    └── azure-deploy.md
```

---

## 🎯 用途別ドキュメント検索

### 「初めて使う」
→ **[README.md](README.md)** → **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)**

### 「全情報を素早く確認したい」
→ **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**

### 「システムの仕組みを理解したい」
→ **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)**

### 「AWSにデプロイしたい」
→ **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** または `./deploy-to-aws.sh`

### 「デモを実施したい」
→ **[DEMO_SCRIPT_FINAL.md](DEMO_SCRIPT_FINAL.md)**

### 「開発履歴を知りたい」
→ **[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)**

### 「Claude Codeで開発する」
→ **[CLAUDE.md](CLAUDE.md)**

### 「DBの詳細を知りたい」
→ **[../aimee-db/DATABASE_STATUS.md](../aimee-db/DATABASE_STATUS.md)**

### 「業務階層を理解したい」
→ **[documents/BUSINESS_HIERARCHY.md](documents/BUSINESS_HIERARCHY.md)**

### 「過去のバグや要件を確認したい」
→ **[documents/reports/](documents/reports/)**

---

## 🔗 外部リソース

- **システム構成図**: [diagrams.net](https://app.diagrams.net/?splash=0#G1kBIJvslm_yRlK2QyCbrDwr9GZnJFTb3X)
- **全体概要**: [Notion](https://pouncing-attic-dd0.notion.site/24154d8b9bc0807c8dfbc7278e5655cf)

---

## 🚀 クイックコマンド

### ローカル開発

```bash
# Docker起動（推奨）
./docker-start-all.sh

# ローカル起動（開発用）
./start_all.sh

# 状態確認
./docker-check-status.sh
```

### AWS本番環境

```bash
# デプロイ
./deploy-to-aws.sh

# アクセス
open http://43.207.175.35:8501
```

### テスト

```bash
# APIテスト実行（Q1～Q6）
python3 run_api_test.py

# 結果確認
cat api_test_results.json
```

### デバッグモード

```bash
# デバッグ情報付きで起動
open http://localhost:8501/?debug=1
```

デバッグモードでは以下が表示されます：
- 意図解析結果（Intent Type、Location、Process）
- 実行されたSQL文
- RAG検索結果と類似度スコア
- スキルマッチング詳細
- 処理時間内訳

---

## 🧪 テスト質問集（Q1～Q6）

詳細は **[README.md](README.md)** の「テスト質問例」セクションを参照

**Q1**: 納期20分前に処理完了
**Q2**: 移動元への影響分析
**Q3**: 業務間移動
**Q4**: 完了時刻予測
**Q5**: 工程別最適配置
**Q6**: 遅延リスク検出

---

## 📊 プロジェクト統計

### マスタードキュメント
- ルート: 8ファイル
- documents: 7ファイル（+レポート）
- 合計: 約170KB

### スクリプト
- デプロイ: 1ファイル
- Docker: 5ファイル
- ローカル: 4ファイル

### フロントエンド
- Python: 4ファイル
- 設定: 3ファイル

---

## 🔄 ドキュメント更新履歴

### 2025-10-26
- ✅ ファイル整理実施（26件削除）
- ✅ 00_INDEX.md作成（このファイル）
- ✅ マスタードキュメント整理完了
- ✅ 承認・否認機能DB保存対応

### 2025-10-24
- ✅ スキルベースマッチング実装
- ✅ QUICK_REFERENCE.md作成
- ✅ documentsフォルダ整理
- ✅ DATABASE_STATUS.md作成
- ✅ deploy-to-aws.sh作成

---

**作成日**: 2025-10-26
**管理者**: 開発チーム
