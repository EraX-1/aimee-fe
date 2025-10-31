# AIMEE AWS環境デプロイガイド

**最終更新**: 2025-11-01
**バージョン**: 2.0.0

---

## 📋 目次

1. [AWS環境概要](#aws環境概要)
2. [ワンコマンドデプロイ](#ワンコマンドデプロイ)
3. [個別デプロイ](#個別デプロイ)
4. [デプロイ後の確認](#デプロイ後の確認)
5. [トラブルシューティング](#トラブルシューティング)

---

## AWS環境概要

### 構成

```
[フロントエンド EC2] ← ユーザー
43.207.175.35:8501
   ↓ API呼び出し
[バックエンド EC2]
54.150.242.233:8002
   ├─ FastAPI
   ├─ Ollama (gemma2:2b, gemma3:4b)
   ├─ ChromaDB
   └─ Redis
   ↓ DB接続
[AWS RDS MySQL]
aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306
```

### EC2インスタンス

| 役割 | IP | ポート | ディレクトリ |
|------|-------------|-------|------------|
| フロントエンド | 43.207.175.35 | 8501 | ~/aimee-fe |
| バックエンド | 54.150.242.233 | 8002 | ~/aimee-be |

### RDS MySQL

```
エンドポイント: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com
ポート: 3306
ユーザー: admin
パスワード: Aimee2024!RDS
データベース: aimee_db
```

### 本番環境URL

- **フロントエンド**: http://43.207.175.35:8501
- **バックエンドAPI**: http://54.150.242.233:8002
- **APIドキュメント**: http://54.150.242.233:8002/docs

---

## ワンコマンドデプロイ

### 初回のみ: スクリプト準備

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 改行コード修正（Windowsで編集した場合）
sed -i '' 's/\r$//' deploy-to-aws.sh

# 実行権限付与
chmod +x deploy-to-aws.sh
```

### 全体デプロイ（フロントエンド + バックエンド）

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./deploy-to-aws.sh
```

**所要時間**: 約15分

**自動実行される処理**:
1. SSH接続確認
2. ソースコードのアーカイブ作成
3. EC2への転送
4. docker-compose.yml更新（platform: amd64）
5. コンテナビルド・起動
6. 動作確認テスト

---

## 個別デプロイ

### フロントエンドのみデプロイ

```bash
./deploy-to-aws.sh frontend
```

**処理内容**:
1. frontend/のアーカイブ作成
2. EC2 (43.207.175.35)への転送
3. 既存コンテナ停止
4. 新コード展開
5. Dockerビルド・起動

**所要時間**: 約5分

### バックエンドのみデプロイ

```bash
./deploy-to-aws.sh backend
```

**処理内容**:
1. app/, scripts/等のアーカイブ作成
2. EC2 (54.150.242.233)への転送
3. 既存コンテナ停止
4. 新コード展開
5. .env設定（RDS接続情報）
6. 全サービス起動（API, Ollama, ChromaDB, Redis, MySQL）

**所要時間**: 約10分

---

## デプロイ後の確認

### 1. コンテナ起動確認

```bash
# フロントエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "docker ps"
```

**期待される出力**:
```
CONTAINER ID   IMAGE            STATUS    PORTS
xxxxx          aimee-frontend   Up        0.0.0.0:8501->8501/tcp
```

```bash
# バックエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker ps"
```

**期待される出力** (6つのコンテナ):
```
aimee-be-api-1          Up  0.0.0.0:8002->8002/tcp
aimee-be-ollama-main-1  Up  11435/tcp
aimee-be-ollama-light-1 Up  11433/tcp
aimee-be-chromadb-1     Up  8003/tcp
aimee-be-redis-1        Up  6380/tcp
aimee-be-mysql-1        Up  3306/tcp
```

### 2. ヘルスチェック

```bash
# APIヘルスチェック
curl http://54.150.242.233:8002/api/v1/health
```

**期待される出力**:
```json
{
  "status": "healthy",
  "timestamp": "..."
}
```

### 3. チャット機能テスト

```bash
curl -X POST http://54.150.242.233:8002/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。",
    "context": {},
    "session_id": "test-session"
  }'
```

**期待される応答**:
```json
{
  "response": "✅ 現在のリソースで対応可能です...",
  "suggestion": {...},
  "timestamp": "..."
}
```

### 4. フロントエンドアクセステスト

ブラウザで以下のURLにアクセス:
```
http://43.207.175.35:8501
```

**確認項目**:
- [ ] チャット画面が表示される
- [ ] 質問を入力できる
- [ ] AIが応答する
- [ ] 配置提案カードが表示される（不足がある場合）

### 5. ログ確認

```bash
# フロントエンドログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend --tail=50"

# バックエンドAPIログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=50"

# Ollamaログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-ollama-main-1 --tail=50"
```

---

## RDSデータ投入

### EC2経由でRDSにデータ投入

```bash
# EC2にSSH接続
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233

# EC2上でMySQLクライアント使用
mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db < ~/aimee-be/real_data_with_mock_names.sql

# 確認
mysql -u admin -p'Aimee2024!RDS' \
  -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  aimee_db -e "SELECT COUNT(*) FROM operators;"
```

### ローカルからRDSにデータ投入

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

---

## トラブルシューティング

### デプロイスクリプトがエラーで停止

#### 症状: SSH接続エラー
```
❌ フロントエンドサーバーに接続できません
```

#### 対処法

```bash
# SSHキー権限確認
ls -l ~/.ssh/aimee-key.pem
chmod 400 ~/.ssh/aimee-key.pem

# 手動接続テスト
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233
```

### コンテナが起動しない

#### 症状: docker psで表示されない

#### 対処法

```bash
# ログ確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=100"

# エラー内容を確認してコンテナ再起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose restart api"

# 全コンテナ再起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose restart"
```

### APIが応答しない

#### 症状: ヘルスチェックが失敗

#### 対処法

```bash
# 依存サービスの確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker ps | grep aimee-be"

# Ollama起動確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker exec aimee-be-ollama-main-1 ollama list"

# モデルが見つからない場合
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker exec aimee-be-ollama-main-1 ollama pull gemma2:2b && \
     docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b"

# RDS接続確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 | grep -i 'database\|rds'"
```

### フロントエンドからバックエンドに接続できない

#### 症状: チャット機能が動作しない

#### 確認

```bash
# バックエンドが起動しているか
curl http://54.150.242.233:8002/api/v1/health

# フロントエンドの設定確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cat ~/aimee-fe/frontend/src/utils/api_client.py | grep 'AIMEE_API_URL'"
```

**期待される設定**: `http://54.150.242.233:8002` または環境変数

---

## ロールバック

### 手動ロールバック

```bash
# バックエンド停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down"

# フロントエンド停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down"
```

### 特定バージョンへのロールバック

```bash
# ローカルでコミットを切り替え
git checkout <previous-commit-hash>

# 再デプロイ
./deploy-to-aws.sh

# 元に戻す
git checkout main
```

---

## デプロイ前チェックリスト

### ローカル環境で実施

- [ ] ローカルでAPIが正常動作している
- [ ] バックエンドが起動している（http://localhost:8002/docs）
- [ ] フロントエンドが起動している（http://localhost:8501）
- [ ] データベースにデータが投入されている
- [ ] APIテストが成功している（精度95%以上）

### デプロイ実施

- [ ] `./deploy-to-aws.sh` を実行
- [ ] エラーなく完了することを確認
- [ ] 本番環境URLにアクセス
- [ ] チャット機能をテスト

---

## デプロイ後の確認ポイント

### 必須確認事項

1. **フロントエンド**
   - [ ] http://43.207.175.35:8501 にアクセスできる
   - [ ] チャット画面が表示される

2. **バックエンド**
   - [ ] http://54.150.242.233:8002/api/v1/health が "healthy"
   - [ ] http://54.150.242.233:8002/docs でAPIドキュメントが表示される

3. **AI機能**
   - [ ] 質問に対してAIが応答する
   - [ ] 4階層構造の配置提案が生成される
   - [ ] 異なる工程間移動が提案される（エントリ2 → エントリ1）

4. **全サービス起動**
   - [ ] API（FastAPI）
   - [ ] Ollama（gemma2:2b, gemma3:4b）
   - [ ] ChromaDB
   - [ ] Redis
   - [ ] MySQL

---

## Tips

### デプロイ時間の目安

- フロントエンドのみ: 約5分
- バックエンドのみ: 約10分
- 全体: 約15分

### バックグラウンド実行

```bash
# ログを見ながら実行
./deploy-to-aws.sh 2>&1 | tee deploy.log

# バックグラウンドで実行
nohup ./deploy-to-aws.sh > deploy.log 2>&1 &

# 進捗確認
tail -f deploy.log
```

### ログ収集

問題が発生した場合、以下のコマンドでログを収集：

```bash
# フロントエンドログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend --tail=200" > frontend.log

# バックエンドAPIログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=200" > backend-api.log

# 全コンテナ状態
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker ps -a" > containers.log
```

---

## 📚 関連ドキュメント

- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - DBセットアップ方法
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - ローカル起動方法
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - システムアーキテクチャ
- **[README.md](../README.md)** - プロジェクト概要
