# AIMEE システム完全インストールガイド

## 📋 目次
1. [前提条件](#前提条件)
2. [データベース (aimee-db) セットアップ](#データベース-aimee-db-セットアップ)
3. [バックエンド (aimee-be) セットアップ](#バックエンド-aimee-be-セットアップ)
4. [フロントエンド (aimee-fe) セットアップ](#フロントエンド-aimee-fe-セットアップ)
5. [システム起動と動作確認](#システム起動と動作確認)
6. [トラブルシューティング](#トラブルシューティング)
7. [データメンテナンス](#データメンテナンス)

---

## 前提条件

### 必須ソフトウェア

#### 1. Docker Desktop
```bash
# インストール確認
docker --version
docker-compose --version

# 起動確認
docker info
```

**推奨バージョン**: Docker 20.10以上、Docker Compose 2.0以上

#### 2. MySQL 8.0
```bash
# インストール確認
mysql --version

# 起動確認
mysql.server status

# 起動していない場合
mysql.server start
```

#### 3. Python 3.12以上
```bash
# インストール確認
python3 --version

# pipアップグレード
python3 -m pip install --upgrade pip
```

#### 4. Git
```bash
# インストール確認
git --version
```

---

## データベース (aimee-db) セットアップ

### ステップ1: リポジトリクローン

```bash
cd /Users/umemiya/Desktop/erax
git clone <aimee-db-repository-url> aimee-db
cd aimee-db
```

### ステップ2: Python依存関係インストール

```bash
pip3 install -r requirements.txt
```

**requirements.txt**:
```
mysql-connector-python==8.0.33
pandas==2.1.0
SQLAlchemy==2.0.20
chardet==5.2.0
```

### ステップ3: MySQLユーザーとデータベース作成

```bash
# MySQLにrootでログイン
mysql -u root -h 127.0.0.1

# 以下をMySQLコンソールで実行
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

-- 終了
EXIT;
```

### ステップ4: スキーマ作成

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# スキーマ適用
mysql -u root -h 127.0.0.1 aimee_db < schema.sql

# テーブル確認
mysql -u root -h 127.0.0.1 aimee_db -e "SHOW TABLES;"
```

**期待される出力**: 20個のテーブル
```
businesses
locations
operators
operator_process_capabilities
processes
approval_history
...
```

### ステップ5: 実データインポート

#### オプションA: バックアップファイルから復元 (推奨)

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# 1. approval_historyテーブル作成
mysql -u root -h 127.0.0.1 aimee_db < approval_history_table.sql

# 2. バックアップファイルから実データを抽出してインポート
python3 << 'EOF'
from config import db_manager
import re

print("実データをインポートします...")

# バックアップファイルから実オペレータを抽出
with open('real_data_complete_with_data.sql.backup', 'r', encoding='utf-8') as f:
    content = f.read()

# operatorsのINSERT文を抽出
pattern = r"\('(a\d{7})','([^']+)','([^']+)'"
matches = re.findall(pattern, content)

# マクロマン除外、100名を使用
real_ops = [(op_id, name, loc_id) for op_id, name, loc_id in matches if 'ﾏｸﾛﾏﾝ' not in name][:100]

print(f"抽出: {len(real_ops)}名")

# 拠点を6拠点に分散
locations = ['91', '51', '42', '41', '31', '61']  # 札幌、品川、本町東、西梅田、沖縄、佐世保

# オペレータインポート
values_list = []
for i, (op_id, name, _) in enumerate(real_ops):
    new_loc = locations[i % len(locations)]
    values_list.append(f"('{op_id}', '{name}', '{new_loc}', '0C-66-66-5A-5A-6C-E8-52-FE-FE-CB-45-79-A8-9F-33', '1', 1, NULL, NOW(), NOW())")

if values_list:
    sql = f"INSERT INTO operators (operator_id, operator_name, location_id, password_hash, belong_code, is_valid, created_by, created_at, updated_at) VALUES {','.join(values_list)}"
    db_manager.execute_query(sql, fetch=False)
    print(f"✅ オペレータ {len(values_list)}名インポート完了")

# スキル情報を付与
import random

operators_data = db_manager.execute_query("SELECT operator_id, location_id FROM operators WHERE is_valid = 1")
processes_data = db_manager.execute_query("""
    SELECT p.business_id, p.process_id, p.level_id
    FROM processes p
    INNER JOIN businesses b ON p.business_id = b.business_id
    WHERE b.business_category = 'SS'
      AND b.business_name = '新SS(W)'
      AND p.process_name IN ('エントリ1', 'エントリ2', '補正', 'SV補正', '目検')
""")

skills = []
for op in operators_data:
    num_skills = random.randint(1, 3)
    selected = random.sample(processes_data, min(num_skills, len(processes_data)))
    for proc in selected:
        skills.append((op['operator_id'], proc['business_id'], proc['process_id'], proc['level_id'], op['location_id']))

# スキル一括インポート
batch_size = 100
for i in range(0, len(skills), batch_size):
    batch = skills[i:i+batch_size]
    values = [f"('{op}', '{bus}', '{proc}', {lvl}, 0, '{loc}')" for op, bus, proc, lvl, loc in batch]
    sql = f"INSERT IGNORE INTO operator_process_capabilities (operator_id, business_id, process_id, work_level, auto_flag, location_id) VALUES {','.join(values)}"
    db_manager.execute_query(sql, fetch=False)

print(f"✅ スキル情報 {len(skills)}件インポート完了")
print("\n実データインポート完了！")
EOF
```

#### オプションB: CSVファイルから復元 (資料フォルダがある場合)

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# 資料フォルダを配置
# /Users/umemiya/Desktop/erax/aimee-db/資料/

# インポートスクリプト実行
python3 import_all_real_data.py
```

### ステップ6: データベース接続確認

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

python3 -c "
from config import db_manager

# 接続確認
result = db_manager.execute_query('SELECT DATABASE() as db, USER() as user')
print(f'接続成功: DB={result[0][\"db\"]}, User={result[0][\"user\"]}')

# データ確認
result = db_manager.execute_query('SELECT COUNT(*) as cnt FROM operators WHERE is_valid = 1')
print(f'オペレータ数: {result[0][\"cnt\"]}名')

result = db_manager.execute_query('SELECT COUNT(*) as cnt FROM operator_process_capabilities')
print(f'スキル数: {result[0][\"cnt\"]}件')

result = db_manager.execute_query('SELECT COUNT(*) as cnt FROM businesses')
print(f'業務数: {result[0][\"cnt\"]}件')
"
```

**期待される出力**:
```
接続成功: DB=aimee_db, User=aimee_user@localhost
オペレータ数: 100名
スキル数: 191件
業務数: 12件
```

---

## バックエンド (aimee-be) セットアップ

### ステップ1: リポジトリクローン

```bash
cd /Users/umemiya/Desktop/erax
git clone <aimee-be-repository-url> aimee-be
cd aimee-be
```

### ステップ2: 環境変数設定

`.env` ファイルを作成:

```bash
cd /Users/umemiya/Desktop/erax/aimee-be

cat > .env << 'EOF'
# アプリケーション設定
APP_NAME=AIMEE-Backend
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# API設定
HOST=0.0.0.0
PORT=8002
API_V1_PREFIX=/api/v1

# データベース設定
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@host.docker.internal:3306/aimee_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# LLM設定 (Ollama)
OLLAMA_LIGHT_HOST=ollama-light
OLLAMA_LIGHT_PORT=11434
INTENT_MODEL=qwen2:0.5b

OLLAMA_MAIN_HOST=ollama-main
OLLAMA_MAIN_PORT=11434
MAIN_MODEL=gemma3:4b

# ChromaDB設定
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
CHROMADB_EXTERNAL_PORT=8003

# Redis設定
REDIS_URL=redis://redis:6379/0

# CORS設定
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173", "http://localhost:8501"]
EOF
```

### ステップ3: Dockerイメージビルド

```bash
cd /Users/umemiya/Desktop/erax/aimee-be

# Docker Composeでビルド＆起動
docker-compose up -d --build

# 起動確認 (約60秒待つ)
sleep 60
docker-compose ps
```

**期待される出力**:
```
aimee-be-api-1            Up 1 minute    0.0.0.0:8002->8002/tcp
aimee-be-chromadb-1       Up 1 minute    0.0.0.0:8003->8000/tcp
aimee-be-redis-1          Up 1 minute (healthy)
aimee-be-ollama-light-1   Up 1 minute
aimee-be-ollama-main-1    Up 1 minute
```

### ステップ4: Ollamaモデルダウンロード

```bash
cd /Users/umemiya/Desktop/erax/aimee-be

# 軽量モデル (意図解析用)
docker exec aimee-be-ollama-light-1 ollama pull qwen2:0.5b

# メインモデル (応答生成用)
docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b

# モデル確認
docker exec aimee-be-ollama-light-1 ollama list
docker exec aimee-be-ollama-main-1 ollama list
```

**期待される出力**:
```
NAME            ID              SIZE      MODIFIED
qwen2:0.5b      6f48b936a09f    352 MB    X days ago
gemma3:4b       a2af6cc3eb7f    3.3 GB    X days ago
```

### ステップ5: API動作確認

```bash
# ヘルスチェック
curl http://localhost:8002/api/v1/health

# APIドキュメント確認
open http://localhost:8002/docs
```

**期待される出力**:
```json
{
  "status": "healthy",
  "app": "AIMEE-Backend",
  "version": "1.0.0",
  "environment": "development"
}
```

### ステップ6: データベース接続確認

```bash
# バックエンドからDB接続確認
curl http://localhost:8002/api/v1/status
```

---

## フロントエンド (aimee-fe) セットアップ

### ステップ1: リポジトリクローン

```bash
cd /Users/umemiya/Desktop/erax
git clone <aimee-fe-repository-url> aimee-fe
cd aimee-fe
```

### ステップ2: 環境変数設定

フロントエンドは環境変数ファイル不要ですが、`api_client.py`でバックエンドURLを確認:

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# バックエンドURL確認
grep "AIMEE_API_URL" frontend/src/utils/api_client.py
```

**デフォルト**: `http://localhost:8002`

### ステップ3: Dockerイメージビルド

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# Docker Composeでビルド＆起動
docker-compose up -d --build

# 起動確認 (約30秒待つ)
sleep 30
docker-compose ps
```

**期待される出力**:
```
aimee-frontend   Up 30 seconds (healthy)   0.0.0.0:8501->8501/tcp
```

### ステップ4: フロントエンド動作確認

```bash
# ブラウザでアクセス
open http://localhost:8501

# または curl で確認
curl http://localhost:8501
```

---

## システム起動と動作確認

### クイックスタート (全体起動)

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 全コンテナ一括起動
./docker-start-all.sh

# 起動確認
./docker-check-status.sh
```

**期待される出力**:
```
=== AIMEEシステム状態 ===
✅ バックエンドAPI (8002番ポート): 起動中
✅ フロントエンド (8501番ポート): 起動中
✅ MySQL: 接続可能
✅ ChromaDB: 起動中
✅ Redis: 起動中
✅ Ollama Light: モデル準備完了
✅ Ollama Main: モデル準備完了
```

### 個別起動

#### バックエンドのみ
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./docker-start-backend.sh
```

#### フロントエンドのみ
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./docker-start-frontend.sh
```

### 停止

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./docker-stop-all.sh
```

---

## 動作確認テスト

### 1. データベース確認

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

python3 << 'EOF'
from config import db_manager

# オペレータ数確認
result = db_manager.execute_query('SELECT COUNT(*) as cnt FROM operators WHERE is_valid = 1')
print(f'オペレータ: {result[0]["cnt"]}名')

# 拠点別オペレータ数
result = db_manager.execute_query("""
    SELECT l.location_name, COUNT(DISTINCT o.operator_id) as cnt
    FROM operators o
    LEFT JOIN locations l ON o.location_id = l.location_id
    WHERE o.is_valid = 1
    GROUP BY l.location_name
    ORDER BY cnt DESC
""")
print('\n拠点別オペレータ数:')
for row in result:
    print(f'  {row["location_name"]}: {row["cnt"]}名')

# スキル数確認
result = db_manager.execute_query("""
    SELECT b.business_name, p.process_name, COUNT(*) as cnt
    FROM operator_process_capabilities opc
    INNER JOIN businesses b ON opc.business_id = b.business_id
    INNER JOIN processes p ON opc.business_id = p.business_id AND opc.process_id = p.process_id
    WHERE b.business_category = 'SS'
      AND b.business_name = '新SS(W)'
    GROUP BY b.business_name, p.process_name
    ORDER BY p.process_name
""")
print('\nSS>新SS(W)のスキル保有者数:')
for row in result:
    print(f'  {row["process_name"]}: {row["cnt"]}名')
EOF
```

**期待される出力**:
```
オペレータ: 100名

拠点別オペレータ数:
  札幌: 17名
  品川: 17名
  本町東: 17名
  西梅田: 17名
  沖縄: 16名
  佐世保: 16名

SS>新SS(W)のスキル保有者数:
  エントリ1: 20名
  エントリ2: 15名
  補正: 18名
  SV補正: 12名
  目検: 10名
```

### 2. バックエンドAPI確認

```bash
# ヘルスチェック
curl http://localhost:8002/api/v1/health

# アラートチェック
curl http://localhost:8002/api/v1/alerts/check

# 承認待ち一覧
curl http://localhost:8002/api/v1/approvals
```

### 3. フロントエンド確認

ブラウザで `http://localhost:8501` にアクセス:

1. **チャット画面が表示される**
2. **サイドバーに3つのタブ**:
   - 💬 配置調整アシスタント
   - ✅ 配置承認
   - 🚨 アラート表示

### 4. エンドツーエンドテスト

フロントエンドのチャット画面で以下を入力:

```
札幌のSSの新SS(W)のOCR対象のエントリ1が人員不足で遅延しています。
佐世保から応援を出せますか?
```

**期待される応答** (約10〜15秒):
```
「SS」の「新SS(W)」の「OCR対象」の「エントリ1」において、
佐世保から萩野　裕子さんを札幌へ配置転換することを提案します。
```

**提案カード**:
- 移動元: 佐世保
- 移動先: 札幌
- 対象者: 萩野　裕子さん (実オペレータ名)
- 信頼度: 85%

---

## トラブルシューティング

### 問題1: MySQLに接続できない

```bash
# MySQL起動確認
mysql.server status

# 起動していない場合
mysql.server start

# 接続テスト
mysql -u aimee_user -p'Aimee2024!' -h 127.0.0.1 aimee_db -e "SELECT 1"
```

### 問題2: Dockerコンテナが起動しない

```bash
# Docker Desktop起動確認
docker info

# ポート競合確認
lsof -i:8002  # バックエンドAPI
lsof -i:8501  # フロントエンド
lsof -i:3306  # MySQL

# 競合プロセスをkill
kill -9 $(lsof -ti:8002)
```

### 問題3: Ollamaモデルがダウンロードされていない

```bash
cd /Users/umemiya/Desktop/erax/aimee-be

# モデル一覧確認
docker exec aimee-be-ollama-light-1 ollama list
docker exec aimee-be-ollama-main-1 ollama list

# モデルが空の場合、手動ダウンロード
docker exec aimee-be-ollama-light-1 ollama pull qwen2:0.5b
docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b
```

### 問題4: チャット応答が遅い・タイムアウト

```bash
# Ollama動作確認
curl http://localhost:11433/api/tags
curl http://localhost:11435/api/tags

# コンテナログ確認
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose logs -f api
docker-compose logs -f ollama-light
docker-compose logs -f ollama-main
```

**対策**:
- タイムアウト設定を延長 (`api_client.py`: timeout=180秒)
- Ollamaコンテナを再起動: `docker-compose restart ollama-light ollama-main`

### 問題5: オペレータデータが表示されない

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# データ確認
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as cnt FROM operators WHERE is_valid = 1')
print(f'有効なオペレータ: {result[0][\"cnt\"]}名')
"

# 0名の場合、実データを再インポート
python3 << 'EOF'
# (上記の実データインポートスクリプトを実行)
EOF
```

---

## データメンテナンス

### 定期バックアップ

#### 1. データベース全体バックアップ

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# バックアップ作成
mysqldump -u root -h 127.0.0.1 aimee_db > backup_$(date +%Y%m%d_%H%M%S).sql

# バックアップ確認
ls -lh backup_*.sql
```

#### 2. 重要テーブルのみバックアップ

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# approval_historyのみバックアップ
mysqldump -u root -h 127.0.0.1 aimee_db approval_history > approval_history_backup.sql

# オペレータ関連のみバックアップ
mysqldump -u root -h 127.0.0.1 aimee_db operators operator_process_capabilities > operators_backup.sql
```

### データリストア

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# 全体リストア
mysql -u root -h 127.0.0.1 aimee_db < backup_20251009_034200.sql

# 特定テーブルのみリストア
mysql -u root -h 127.0.0.1 aimee_db < approval_history_backup.sql
```

### データクリーンアップ

#### Mockデータ削除

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

python3 << 'EOF'
from config import db_manager

# Mockデータ削除
queries = [
    "DELETE FROM operator_process_capabilities WHERE operator_id LIKE 'demo%'",
    "DELETE FROM operator_process_capabilities WHERE operator_id LIKE 'kenpo%'",
    "DELETE FROM operators WHERE operator_id LIKE 'demo%'",
    "DELETE FROM operators WHERE operator_id LIKE 'kenpo%'",
]

for q in queries:
    db_manager.execute_query(q, fetch=False)

print("✅ Mockデータ削除完了")
EOF
```

#### 古い承認履歴削除 (90日以上前)

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

python3 << 'EOF'
from config import db_manager

# 90日以上前の承認履歴を削除
db_manager.execute_query("""
    DELETE FROM approval_history
    WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY)
""", fetch=False)

print("✅ 古い承認履歴削除完了")
EOF
```

### データ整合性チェック

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

python3 << 'EOF'
from config import db_manager

print("データ整合性チェック...")

# 1. 孤立したスキル情報チェック
result = db_manager.execute_query("""
    SELECT COUNT(*) as cnt
    FROM operator_process_capabilities opc
    LEFT JOIN operators o ON opc.operator_id = o.operator_id
    WHERE o.operator_id IS NULL
""")
print(f"孤立スキル: {result[0]['cnt']}件")

# 2. 無効なオペレータのスキル削除
db_manager.execute_query("""
    DELETE opc FROM operator_process_capabilities opc
    INNER JOIN operators o ON opc.operator_id = o.operator_id
    WHERE o.is_valid = 0
""", fetch=False)
print("✅ 無効なオペレータのスキルを削除")

# 3. 拠点不一致チェック
result = db_manager.execute_query("""
    SELECT COUNT(*) as cnt
    FROM operator_process_capabilities opc
    INNER JOIN operators o ON opc.operator_id = o.operator_id
    WHERE opc.location_id != o.location_id
""")
print(f"拠点不一致: {result[0]['cnt']}件")

# 4. 拠点を一致させる
db_manager.execute_query("""
    UPDATE operator_process_capabilities opc
    INNER JOIN operators o ON opc.operator_id = o.operator_id
    SET opc.location_id = o.location_id
    WHERE opc.location_id != o.location_id
""", fetch=False)
print("✅ 拠点不一致を修正")

print("\nデータ整合性チェック完了")
EOF
```

---

## 定期メンテナンススクリプト

### daily_maintenance.sh (毎日実行推奨)

```bash
#!/bin/bash
# AIMEE 日次メンテナンススクリプト

cd /Users/umemiya/Desktop/erax/aimee-db

DATE=$(date +%Y%m%d)
BACKUP_DIR="/Users/umemiya/Desktop/erax/backups"

mkdir -p $BACKUP_DIR

echo "=== AIMEE 日次メンテナンス ==="
echo "実行日時: $(date)"

# 1. データベースバックアップ
echo "1. データベースバックアップ中..."
mysqldump -u root -h 127.0.0.1 aimee_db > $BACKUP_DIR/aimee_db_$DATE.sql
echo "✅ バックアップ完了: $BACKUP_DIR/aimee_db_$DATE.sql"

# 2. 古いバックアップ削除 (30日以上前)
echo "2. 古いバックアップ削除中..."
find $BACKUP_DIR -name "aimee_db_*.sql" -mtime +30 -delete
echo "✅ 古いバックアップ削除完了"

# 3. データ整合性チェック
echo "3. データ整合性チェック中..."
python3 << 'PYTHON_EOF'
from config import db_manager

# 無効オペレータのスキル削除
db_manager.execute_query("""
    DELETE opc FROM operator_process_capabilities opc
    INNER JOIN operators o ON opc.operator_id = o.operator_id
    WHERE o.is_valid = 0
""", fetch=False)

# 拠点一致
db_manager.execute_query("""
    UPDATE operator_process_capabilities opc
    INNER JOIN operators o ON opc.operator_id = o.operator_id
    SET opc.location_id = o.location_id
    WHERE opc.location_id != o.location_id
""", fetch=False)

print("✅ データ整合性チェック完了")
PYTHON_EOF

# 4. ログローテーション
echo "4. ログローテーション中..."
cd /Users/umemiya/Desktop/erax/aimee-be
find . -name "*.log" -mtime +7 -delete
echo "✅ 古いログ削除完了"

echo ""
echo "=== メンテナンス完了 ==="
echo "次回実行: $(date -v+1d)"
```

**実行方法**:
```bash
chmod +x daily_maintenance.sh
./daily_maintenance.sh
```

**cron設定** (毎日午前3時実行):
```bash
crontab -e

# 以下を追加
0 3 * * * /Users/umemiya/Desktop/erax/aimee-db/daily_maintenance.sh >> /tmp/aimee_maintenance.log 2>&1
```

---

## システム再構築手順

システムを完全にクリーンな状態から再構築する場合:

### ステップ1: 既存環境の削除

```bash
# Docker コンテナ・ボリューム削除
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose down -v

cd /Users/umemiya/Desktop/erax/aimee-fe
docker-compose down -v

# データベース削除
mysql -u root -h 127.0.0.1 -e "DROP DATABASE IF EXISTS aimee_db"
mysql -u root -h 127.0.0.1 -e "DROP USER IF EXISTS 'aimee_user'@'localhost'"
```

### ステップ2: 再構築

上記の **データベースセットアップ** から順に実行

---

## 📋 チェックリスト

### 初回セットアップ時

- [ ] Docker Desktop インストール・起動
- [ ] MySQL 8.0 インストール・起動
- [ ] Python 3.12以上 インストール
- [ ] リポジトリクローン (aimee-db, aimee-be, aimee-fe)
- [ ] MySQLユーザー・データベース作成
- [ ] スキーマ適用 (`schema.sql`)
- [ ] approval_historyテーブル作成
- [ ] 実データインポート (100名)
- [ ] バックエンド `.env` 作成
- [ ] バックエンド Docker起動
- [ ] Ollamaモデルダウンロード (qwen2:0.5b, gemma3:4b)
- [ ] フロントエンド Docker起動
- [ ] 全体動作確認 (`./docker-check-status.sh`)
- [ ] エンドツーエンドテスト (チャット機能)

### 日次メンテナンス

- [ ] データベースバックアップ
- [ ] データ整合性チェック
- [ ] ログローテーション
- [ ] コンテナ状態確認

### 週次メンテナンス

- [ ] 古いバックアップ削除 (30日以上前)
- [ ] 古い承認履歴削除 (90日以上前)
- [ ] Dockerイメージ更新
- [ ] システムリソース確認 (ディスク容量、メモリ)

---

## 📞 サポート

### ログ確認

#### バックエンド
```bash
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose logs -f api
docker-compose logs -f ollama-light
docker-compose logs -f ollama-main
```

#### フロントエンド
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
docker-compose logs -f frontend
```

#### データベース
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
tail -f *.log
```

### システムリソース確認

```bash
# Docker コンテナのリソース使用状況
docker stats

# ディスク容量
df -h

# メモリ使用状況
free -h  # (Linuxの場合)
vm_stat  # (macOSの場合)
```

---

## 📄 関連ドキュメント

- **CLAUDE.md**: プロジェクト詳細情報
- **INTEGRATION.md**: フロント・バックエンド統合ガイド
- **TECHNICAL_SUMMARY.md**: 技術要素まとめ
- **DEMO_SCRIPT_FINAL.md**: デモ動画用台本
- **REAL_DATA_SUCCESS.md**: 実データインポート成功レポート
- **AWS_DEPLOY_GUIDE.md**: AWSデプロイガイド

---

**作成日**: 2025-10-09
**最終更新**: 実データインポート完了後
**バージョン**: 1.0
