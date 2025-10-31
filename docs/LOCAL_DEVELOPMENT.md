# AIMEE ローカル開発環境 起動ガイド

**最終更新**: 2025-11-01
**バージョン**: 2.0.0

---

## 📋 目次

1. [前提条件](#前提条件)
2. [Docker起動（Ollama + ChromaDB）](#docker起動ollama--chromadb)
3. [バックエンド起動](#バックエンド起動)
4. [フロントエンド起動](#フロントエンド起動)
5. [動作確認](#動作確認)
6. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必須条件

✅ データベースが起動していること
```bash
mysql.server status
# 起動していない場合
mysql.server start
```

✅ データが投入されていること
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) FROM progress_snapshots WHERE total_waiting > 0')
print(f'progress_snapshots: {result[0][\"COUNT(*)\"]}件')
"
# 期待値: 584件以上
```

データが不足している場合:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_dummy_data.sh
```

---

## Docker起動（Ollama + ChromaDB）

### ステップ1: Dockerサービス起動

```bash
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose up -d ollama-light ollama-main chromadb
```

**起動するサービス**:
- `ollama-light` - 意図解析用LLM（ポート: 11435）
- `ollama-main` - 応答生成用LLM（ポート: 11435）
- `chromadb` - ベクトルDB（ポート: 8003）

### ステップ2: LLMモデルダウンロード（初回のみ）

```bash
# gemma2:2b（意図解析用）
docker exec aimee-be-ollama-main-1 ollama pull gemma2:2b

# gemma3:4b（応答生成用）
docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b
```

**所要時間**: 約5分（gemma2:2b: 1.6GB、gemma3:4b: 2.5GB）

### ステップ3: 起動確認

```bash
# コンテナ確認
docker ps | grep aimee-be
```

**期待される出力**:
```
aimee-be-ollama-light-1   ... Up   11435/tcp
aimee-be-ollama-main-1    ... Up   11435/tcp
aimee-be-chromadb-1       ... Up   8003/tcp
```

### ステップ4: モデル確認

```bash
# モデルリスト確認
docker exec aimee-be-ollama-main-1 ollama list
```

**期待される出力**:
```
NAME           ID           SIZE    MODIFIED
gemma2:2b      ...          1.6GB   ...
gemma3:4b      ...          2.5GB   ...
```

---

## バックエンド起動

### 方法1: Pythonで直接起動（推奨）

```bash
cd /Users/umemiya/Desktop/erax/aimee-be
python3 start.py
```

**期待される出力**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8002
```

### 方法2: uvicornコマンドで起動

```bash
cd /Users/umemiya/Desktop/erax/aimee-be
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### APIドキュメント確認

ブラウザで以下のURLにアクセス:
```
http://localhost:8002/docs
```

**確認項目**:
- `/api/v1/chat/message` - チャットAPI
- `/api/v1/approvals` - 承認API
- `/api/v1/alerts` - アラートAPI

---

## フロントエンド起動

### ステップ1: フロントエンド起動

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
streamlit run app.py
```

**期待される出力**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### ステップ2: ブラウザアクセス

```
http://localhost:8501
```

---

## 動作確認

### チャット機能テスト

フロントエンドのチャット画面で以下の質問を試します:

#### Q1: 納期最適化
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。
```

**期待される応答**:
```
✅ 現在のリソースで対応可能です

【分析結果】
- 現在時刻: 12:40
- 納期: 15:40（あと180分）
- 残タスク数: 947件
...
```

#### Q4: 完了時刻予測
```
SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか
```

**期待される応答**:
```
📊 処理完了時刻の予測

【SS 15:40受信分】
- 予測完了時刻: 15:40
...
```

### API直接テスト

```bash
curl -X POST http://localhost:8002/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。",
    "context": {},
    "session_id": "test-session"
  }'
```

**期待されるレスポンス**:
```json
{
  "response": "✅ 現在のリソースで対応可能です...",
  "suggestion": null,
  "timestamp": "2025-11-01T12:00:00"
}
```

---

## トラブルシューティング

### バックエンドが起動しない

#### 原因1: ポート8002が使用中

```bash
# ポート使用確認
lsof -i:8002

# プロセスをKill
kill -9 <PID>
```

#### 原因2: DB接続エラー

```bash
# DB接続確認
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "from config import db_manager; print(db_manager.test_connection())"
```

**期待される出力**: `Connection successful!`

#### 原因3: 環境変数未設定

`.env`ファイルを確認:
```bash
cd /Users/umemiya/Desktop/erax/aimee-be
cat .env | grep -E "DATABASE_URL|OLLAMA|CHROMADB"
```

**期待される内容**:
```
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@localhost:3306/aimee_db
OLLAMA_LIGHT_PORT=11435
OLLAMA_MAIN_PORT=11435
INTENT_MODEL=gemma2:2b
MAIN_MODEL=gemma3:4b
CHROMADB_HOST=localhost
CHROMADB_PORT=8003
```

### フロントエンドでAPI接続エラー

#### 確認1: バックエンドが起動しているか

```bash
curl http://localhost:8002/docs
```

#### 確認2: APIのベースURLを確認

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
grep -r "AIMEE_API_URL" src/
```

**期待される設定**: `http://localhost:8002`

### Ollamaが応答しない

#### 確認1: コンテナが起動しているか

```bash
docker ps | grep ollama
```

#### 確認2: モデルがダウンロードされているか

```bash
docker exec aimee-be-ollama-main-1 ollama list
```

モデルが見つからない場合:
```bash
docker exec aimee-be-ollama-main-1 ollama pull gemma2:2b
docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b
```

#### 確認3: Ollamaに接続できるか

```bash
curl http://localhost:11435/api/tags
```

### ChromaDBに接続できない

#### 確認1: コンテナが起動しているか

```bash
docker ps | grep chroma
```

#### 確認2: ChromaDBに接続できるか

```bash
curl http://localhost:8003/api/v1/heartbeat
```

**期待される出力**: `{"nanosecond heartbeat": ...}`

#### 確認3: コレクションがあるか

```bash
python3 << EOF
import chromadb
client = chromadb.HttpClient(host='localhost', port=8003)
collections = client.list_collections()
print([c.name for c in collections])
EOF
```

**期待される出力**: `['aimee_knowledge']`

コレクションがない場合:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 import_manager_knowledge_to_chroma.py
```

### Q1で「現在のリソースで対応可能」としか表示されない

#### 原因: progress_snapshotsが空または不足

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as c FROM progress_snapshots WHERE total_waiting > 0;')
print(f'progress_snapshots: {result[0][\"c\"]}件')
"
```

**期待値**: 584件以上

不足している場合:
```bash
python3 extract_and_import_snapshots.py
```

---

## 開発Tips

### デバッグモード

フロントエンドでデバッグ情報を表示:
```
http://localhost:8501/?debug=1
```

**表示される情報**:
- Intent Type判定結果
- 実行されたSQL文
- RAG検索結果
- 処理時間内訳

### ログ確認

#### バックエンドログ

```bash
cd /Users/umemiya/Desktop/erax/aimee-be
tail -f logs/app.log
```

#### Dockerログ

```bash
# Ollamaログ
docker logs -f aimee-be-ollama-main-1

# ChromaDBログ
docker logs -f aimee-be-chromadb-1
```

### ホットリロード

バックエンドを`--reload`オプションで起動すると、コード変更時に自動再起動:
```bash
cd /Users/umemiya/Desktop/erax/aimee-be
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

---

## 停止方法

### 全停止

```bash
# Dockerサービス停止
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose down

# バックエンド停止（Ctrl+C）
# フロントエンド停止（Ctrl+C）

# MySQL停止（必要な場合のみ）
mysql.server stop
```

---

## クイックスタート（まとめ）

### 推奨方法: Docker起動スクリプト使用（⭐推奨）

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 全体起動（バックエンド + フロントエンド）
./docker-start-all.sh

# または個別起動
./docker-start-backend.sh   # バックエンドのみ
./docker-start-frontend.sh  # フロントエンドのみ

# 状態確認
./docker-check-status.sh

# 停止
./docker-stop-all.sh

# ブラウザアクセス
open http://localhost:8501
```

**メリット**:
- ✅ 全依存サービスが自動的に起動
- ✅ 本番環境と同じ構成
- ✅ 環境構築が簡単

### 開発者向け: Python直接実行（ホットリロード有効）

コード修正を即座に反映したい場合:

```bash
# 1. DB起動確認
mysql.server status

# 2. 依存サービスのみDockerで起動
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose up -d ollama-main chromadb redis

# 3. バックエンド起動（Pythonで直接）
./scripts/start_backend.sh

# 4. フロントエンド起動（別ターミナル）
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
streamlit run app.py

# 5. ブラウザアクセス
open http://localhost:8501
```

**メリット**:
- ✅ コード変更が即座に反映（--reload）
- ✅ デバッグが容易

---

## 📚 関連ドキュメント

- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - DBセットアップ方法
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - システムアーキテクチャ
- **[INTENT_TYPES.md](INTENT_TYPES.md)** - 9分類の詳細
- **[AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)** - AWSデプロイ方法
- **[README.md](../README.md)** - プロジェクト概要
