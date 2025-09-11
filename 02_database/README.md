# データベース設計ドキュメント

## 📚 ドキュメント構成

### 1. design/ - 設計ドキュメント
- **01_overview.md**: データベース設計の全体像
  - 20テーブルの概要説明
  - バッチ2・バッチ3の役割分担
  - 技術スタック

- **02_table_specifications.md**: テーブル詳細仕様
  - 全カラムの業務的説明
  - データ型・制約の技術仕様
  - インデックス・外部キー一覧

### 2. diagrams/ - 図表
- **01_er_diagram.md**: ER図とデータフロー
  - ASCII アートでの関係図
  - テーブル間の関連性
  - データの流れ

### 3. scripts/ - SQLスクリプト
- **init.sql**: DB構築・初期化スクリプト
  - 全テーブルのCREATE文
  - 初期マスタデータ
  - ビュー・ストアドプロシージャ

## 🗂️ テーブル分類

### 共通マスタ（5テーブル）
- locations: 拠点マスタ
- business_types: 業務マスタ  
- processes: 工程マスタ
- teams: チームマスタ
- operators: オペレータマスタ

### バッチ2専用（4テーブル）
配置情報取得エンジン用
- current_assignments: 現在の配置
- operator_skills: スキル情報
- processing_status: 処理状況
- login_status: ログイン状況

### バッチ3専用（3テーブル）
OP実績取得エンジン用
- operator_performance: 個人実績
- location_productivity: 拠点生産性
- workload_trends: 業務量推移

### AI学習用（4テーブル）
- assignment_history: 配置変更履歴
- manager_decisions: 管理者判断
- ai_suggestions: AI提案
- knowledge_embeddings: RAGベクトル

### システム連携（2テーブル）
- data_imports: インポート履歴
- system_notifications: 通知

### UI設定（2テーブル）
- ui_dashboards: ダッシュボード設定
- ui_preferences: ユーザー設定

## 🚀 DB構築手順

```bash
# 1. MySQLにログイン
mysql -u root -p

# 2. データベース作成
CREATE DATABASE aimee_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 3. 初期化スクリプト実行
mysql -u root -p aimee_db < scripts/init.sql
```

## 📊 データベース技術仕様

- **DBMS**: MySQL 8.0+ / PostgreSQL 13+
- **文字コード**: UTF8MB4
- **照合順序**: utf8mb4_unicode_ci
- **エンジン**: InnoDB
- **タイムゾーン**: Asia/Tokyo