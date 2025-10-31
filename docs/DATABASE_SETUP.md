# AIMEE データベースセットアップガイド

**最終更新**: 2025-11-01
**バージョン**: 2.0.0

---

## 📋 目次

1. [データベース概要](#データベース概要)
2. [ダミーデータ vs 本番データ](#ダミーデータ-vs-本番データ)
3. [ローカル環境セットアップ](#ローカル環境セットアップ)
4. [データ投入方法](#データ投入方法)
5. [AWS RDSセットアップ](#aws-rdsセットアップ)
6. [トラブルシューティング](#トラブルシューティング)

---

## データベース概要

### 使用データベース
- **種類**: MySQL 8.0
- **データベース名**: `aimee_db`
- **文字セット**: utf8mb4

### 主要テーブル（20テーブル）

| テーブル | 件数 | 説明 |
|---------|------|------|
| **operators** | 100 | オペレータマスタ |
| **operator_process_capabilities** | 191 | スキル情報 |
| **progress_snapshots** | 832 | 進捗スナップショット（重要） |
| **locations** | 7 | 拠点マスタ |
| **businesses** | 12 | 業務マスタ |
| **processes** | 46 | 工程マスタ |
| **approval_history** | - | 承認履歴 |
| **rag_context** | 5 | 管理者ノウハウ |

---

## ダミーデータ vs 本番データ

### ダミーデータ（モック名）

**特徴**:
- オペレータ名のみモック化（日本人風の仮名）
- その他のデータ（拠点、業務、進捗）は実データ
- 開発・デモ・外部共有に使用

**例**:
```
operator_id: a0301930
operator_name: 竹下　朱美  ← モック名
location_id: 91（札幌）
```

**データソース**: `/Users/umemiya/Desktop/erax/aimee-db/real_data_with_mock_names.sql`

### 本番データ（実名）⚠️ 機密情報

**特徴**:
- 実際のオペレータ名を使用
- 本番環境（AWS RDS）で使用
- セキュリティ厳重管理

**注意**:
- ローカル開発環境では基本的にダミーデータを使用
- 本番データは内部分析のみ

---

## ローカル環境セットアップ

### 前提条件

```bash
# MySQL 8.0がインストールされていること
mysql --version

# MySQLが起動していること
mysql.server status

# 起動していない場合
mysql.server start
```

### ステップ1: データベース作成

```bash
# MySQLにrootでログイン
mysql -u root -h 127.0.0.1
```

```sql
-- データベース作成
DROP DATABASE IF EXISTS aimee_db;
CREATE DATABASE aimee_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- ユーザー作成
DROP USER IF EXISTS 'aimee_user'@'localhost';
CREATE USER 'aimee_user'@'localhost' IDENTIFIED BY 'Aimee2024!';

-- 権限付与
GRANT ALL PRIVILEGES ON aimee_db.* TO 'aimee_user'@'localhost';
FLUSH PRIVILEGES;

-- 確認
SHOW DATABASES LIKE 'aimee_db';
SELECT User, Host FROM mysql.user WHERE User='aimee_user';

EXIT;
```

### ステップ2: スキーマ適用

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# スキーマ作成
mysql -u aimee_user -p'Aimee2024!' aimee_db < schema.sql

# テーブル確認
mysql -u aimee_user -p'Aimee2024!' aimee_db -e "SHOW TABLES;"
```

**期待される出力**: 20個のテーブル

---

## データ投入方法

### 方法1: ワンコマンドで全データ投入（推奨）

#### ダミーデータを投入

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_dummy_data.sh
```

**実行内容**:
1. 自動バックアップ作成
2. 既存データクリア
3. ダミーデータ投入（operators: 100名、progress_snapshots: 832件）
4. ChromaDB投入（aimee_knowledge: 12件）

**所要時間**: 約3分

#### 実名データを投入（内部分析のみ）

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_real_data.sh
```

### 方法2: 手動で個別投入

#### 基本データ投入

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# ダミーデータ投入
mysql -u aimee_user -p'Aimee2024!' aimee_db < real_data_with_mock_names.sql

# 確認
mysql -u aimee_user -p'Aimee2024!' aimee_db -e "SELECT COUNT(*) FROM operators;"
# 期待値: 100
```

#### progress_snapshots投入（重要）

**progress_snapshotsは、納期・残タスク数等の進捗データで、Q1〜Q6の動作に必須です。**

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 extract_and_import_snapshots.py
```

**処理内容**:
1. バックアップファイルから832件抽出
2. aimee_dbに投入

**確認**:
```bash
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as c FROM progress_snapshots WHERE total_waiting > 0;')
print(f'progress_snapshots: {result[0][\"c\"]}件')
"
```

**期待値**: 584件以上

#### ChromaDB投入（管理者ノウハウ）

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 import_manager_knowledge_to_chroma.py
```

**処理内容**:
1. `管理者の判断材料・判断基準等について.txt`を読み込み
2. チャンキング（セクション分割）
3. ChromaDBに投入（aimee_knowledgeコレクション）

**確認**:
```bash
python3 << EOF
import chromadb
client = chromadb.HttpClient(host='localhost', port=8003)
collections = client.list_collections()
for col in collections:
    if 'aimee' in col.name.lower():
        print(f'{col.name}: {col.count()}件')
EOF
```

**期待値**: aimee_knowledge: 12件

---

## AWS RDSセットアップ

### RDS接続情報

```
エンドポイント: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com
ポート: 3306
ユーザー: admin
パスワード: Aimee2024!RDS
データベース名: aimee_db
```

### ローカルからRDSに接続

```bash
mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db
```

### RDSにデータ投入

#### EC2経由で投入（推奨）

```bash
# EC2にSSH接続
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233

# EC2上でMySQLクライアント使用
mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db < real_data_with_mock_names.sql
```

#### ローカルから直接投入

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# スキーマ投入
mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db < schema.sql

# データ投入
mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db < real_data_with_mock_names.sql
```

### RDSデータ確認

```bash
# オペレータ件数確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker exec aimee-be-mysql-1 mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db -e 'SELECT COUNT(*) FROM operators;'"

# progress_snapshots確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker exec aimee-be-mysql-1 mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db -e 'SELECT COUNT(*) FROM progress_snapshots WHERE total_waiting > 0;'"
```

---

## データ検証

### 必須データが投入されているか確認

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager

tables = {
    'operators': 100,
    'operator_process_capabilities': 191,
    'progress_snapshots': 832,
    'locations': 7,
    'businesses': 12,
    'processes': 46
}

print('【データ検証】')
for table, expected in tables.items():
    result = db_manager.execute_query(f'SELECT COUNT(*) as c FROM {table};')
    actual = result[0]['c']
    status = '✅' if actual >= expected else '❌'
    print(f'{status} {table}: {actual}件 (期待値: {expected}件)')
"
```

### ChromaDB検証

```bash
python3 << EOF
import chromadb
client = chromadb.HttpClient(host='localhost', port=8003)

try:
    collection = client.get_collection('aimee_knowledge')
    count = collection.count()
    print(f'✅ ChromaDB: aimee_knowledge = {count}件 (期待値: 12件)')
except:
    print('❌ ChromaDB: aimee_knowledgeコレクションが見つかりません')
EOF
```

---

## トラブルシューティング

### MySQL接続エラー

```bash
# MySQLが起動しているか確認
mysql.server status

# 起動していない場合
mysql.server start

# ユーザー権限確認
mysql -u root -e "SELECT User, Host FROM mysql.user WHERE User='aimee_user';"

# パスワードリセット
mysql -u root -e "ALTER USER 'aimee_user'@'localhost' IDENTIFIED BY 'Aimee2024!';"
```

### progress_snapshotsが空

**症状**: Q1で「現在のリソースで対応可能」としか表示されない

**原因**: progress_snapshotsが投入されていない

**解決方法**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 extract_and_import_snapshots.py
```

### ChromaDBに接続できない

**症状**: RAG検索が動作しない

**確認**:
```bash
# Dockerコンテナ確認
docker ps | grep chroma

# ChromaDBが起動していない場合
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose up -d chromadb

# ポート確認
curl http://localhost:8003/api/v1/heartbeat
```

### データが破損した

**復元方法**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_dummy_data.sh
```

---

## 参考情報

### データファイル一覧

| ファイル名 | サイズ | 説明 |
|-----------|--------|------|
| `schema.sql` | 30KB | テーブル定義 |
| `real_data_with_mock_names.sql` | 3.9MB | ダミーデータ |
| `backups/aimee_db_production_*.sql` | - | バックアップ |

### Python接続設定（config.py）

```python
from config import db_manager

# クエリ実行
result = db_manager.execute_query('SELECT * FROM operators LIMIT 5;')

# 更新クエリ
db_manager.execute_query(
    "INSERT INTO operators (...) VALUES (...);",
    fetch=False
)
```

### 接続情報まとめ

#### ローカル環境
```
ホスト: localhost
ポート: 3306
ユーザー: aimee_user
パスワード: Aimee2024!
データベース: aimee_db
```

#### AWS RDS
```
ホスト: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com
ポート: 3306
ユーザー: admin
パスワード: Aimee2024!RDS
データベース: aimee_db
```

---

## 📚 関連ドキュメント

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - システムアーキテクチャ
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - ローカル起動方法
- **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - AWSデプロイ方法
- **[README.md](../README.md)** - プロジェクト概要
