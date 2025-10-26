# AIMEE AWS デプロイガイド

本番環境（AWS EC2）へのデプロイ手順書

---

## 📋 目次

1. [環境情報](#環境情報)
2. [前提条件](#前提条件)
3. [デプロイ手順](#デプロイ手順)
4. [トラブルシューティング](#トラブルシューティング)
5. [ロールバック手順](#ロールバック手順)

---

## 🌐 環境情報

### 本番環境URL
- **フロントエンド**: http://43.207.175.35:8501
- **バックエンドAPI**: http://54.150.242.233:8002

### EC2インスタンス

#### フロントエンドサーバー
- **IP**: `43.207.175.35`
- **SSHキー**: `~/.ssh/aimee-key.pem`
- **ユーザー**: `ubuntu`
- **ディレクトリ**: `~/aimee-fe`
- **ポート**: `8501`

#### バックエンドサーバー
- **IP**: `54.150.242.233`
- **SSHキー**: `~/.ssh/aimee-key.pem`
- **ユーザー**: `ubuntu`
- **ディレクトリ**: `~/aimee-be`
- **ポート**: `8002`

### RDS MySQL
- **エンドポイント**: `aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306`
- **データベース名**: `aimee_db`
- **ユーザー**: `admin`
- **パスワード**: `Aimee2024!RDS`

---

## ✅ 前提条件

### ローカル環境
```bash
# SSHキーの権限確認
ls -la ~/.ssh/aimee-key.pem
# -r--------と表示されることを確認

# 権限が違う場合は修正
chmod 400 ~/.ssh/aimee-key.pem
```

### EC2への接続確認
```bash
# フロントエンドサーバー
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "echo 'Connected'"

# バックエンドサーバー
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "echo 'Connected'"
```

---

## 🚀 デプロイ手順

### 1. フロントエンドのデプロイ

#### 1-1. ローカルでアーカイブ作成
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 不要なファイルを除外してアーカイブ
tar --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    -czf /tmp/aimee-fe-deploy.tar.gz .

# サイズ確認
ls -lh /tmp/aimee-fe-deploy.tar.gz
```

#### 1-2. EC2に転送
```bash
scp -i ~/.ssh/aimee-key.pem \
    /tmp/aimee-fe-deploy.tar.gz \
    ubuntu@43.207.175.35:~/aimee-fe-new.tar.gz
```

#### 1-3. 既存コンテナを停止
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down"
```

#### 1-4. 新しいコードを展開
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~ && tar -xzf aimee-fe-new.tar.gz -C aimee-fe/"
```

#### 1-5. docker-compose.ymlの確認・修正
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && cat > docker-compose.yml << 'EOF'
version: '3.9'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    platform: linux/amd64
    container_name: aimee-frontend
    ports:
      - \"8501:8501\"
    environment:
      - AIMEE_API_URL=http://54.150.242.233:8002
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    restart: unless-stopped

networks:
  default:
    driver: bridge
EOF
"
```

#### 1-6. コンテナをビルド・起動
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose up -d --build"
```

#### 1-7. 起動確認
```bash
# コンテナ状態確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "docker ps"

# ログ確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend --tail=50"

# アクセステスト
curl -s http://43.207.175.35:8501 | grep -i "streamlit"
```

---

### 2. バックエンドのデプロイ

#### 2-1. ローカルでアーカイブ作成
```bash
cd /Users/umemiya/Desktop/erax/aimee-be

# 必要なファイルのみアーカイブ（データボリュームは除外）
tar --exclude='node_modules' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='chroma-data' \
    --exclude='mysql-data' \
    --exclude='redis-data' \
    --exclude='ollama-*' \
    --exclude='experiments' \
    --exclude='*.tar.gz' \
    -czf /tmp/aimee-be-deploy.tar.gz \
    app Dockerfile.api docker-compose.yml .env start.py requirements.txt

# サイズ確認
ls -lh /tmp/aimee-be-deploy.tar.gz
```

#### 2-2. EC2に転送
```bash
scp -i ~/.ssh/aimee-key.pem \
    /tmp/aimee-be-deploy.tar.gz \
    ubuntu@54.150.242.233:~/aimee-be-new.tar.gz
```

#### 2-3. 既存コンテナを停止
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down"
```

#### 2-4. 新しいコードを展開
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && tar -xzf ~/aimee-be-new.tar.gz"
```

#### 2-5. .envファイルの確認
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && cat .env | head -20"

# DATABASE_URLがRDSを指していることを確認
# DATABASE_URL=mysql+aiomysql://admin:Aimee2024!RDS@aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306/aimee_db
```

#### 2-6. コンテナを起動
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose up -d"
```

#### 2-7. 起動確認
```bash
# コンテナ状態確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker ps"

# APIログ確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=50"

# ヘルスチェック
curl -s http://54.150.242.233:8002/api/v1/health
```

---

### 3. デプロイ後の動作確認

#### 3-1. API疎通確認
```bash
# ヘルスチェック
curl http://54.150.242.233:8002/api/v1/health

# チャット機能
curl -X POST http://54.150.242.233:8002/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"札幌のエントリ1工程が遅延しています","conversation_id":"test123"}'

# 承認一覧
curl http://54.150.242.233:8002/api/v1/approvals

# アラート一覧
curl http://54.150.242.233:8002/api/v1/alerts
```

#### 3-2. フロントエンド動作確認
1. ブラウザで http://43.207.175.35:8501 にアクセス
2. チャット機能をテスト
3. 承認待ち一覧を確認
4. アラート表示を確認

#### 3-3. バックエンドログ確認
```bash
# エラーがないか確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=100 | grep -i error"
```

---

## 🔧 トラブルシューティング

### フロントエンドが起動しない

#### 問題: コンテナが起動しない
```bash
# ログ確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend"

# コンテナを再起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose restart"
```

#### 問題: APIに接続できない
```bash
# 環境変数確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker exec aimee-frontend env | grep AIMEE_API_URL"

# バックエンドへの疎通確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "curl http://54.150.242.233:8002/api/v1/health"
```

### バックエンドが起動しない

#### 問題: APIコンテナがエラー
```bash
# 詳細ログ確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=200"

# 依存サービスの確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker ps -a | grep aimee-be"
```

#### 問題: RDSに接続できない
```bash
# .env確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && grep DATABASE_URL .env"

# RDS接続テスト
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker exec aimee-be-api-1 python -c 'import pymysql; conn = pymysql.connect(host=\"aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com\", user=\"admin\", password=\"Aimee2024!RDS\", database=\"aimee_db\"); print(\"OK\")'"
```

### ポート競合

#### 問題: ポートが既に使用されている
```bash
# フロントエンド (8501)
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "sudo lsof -i:8501"

# バックエンド (8002)
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "sudo lsof -i:8002"

# 既存プロセスを停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down"
```

---

## ⏪ ロールバック手順

### 1. バックアップからの復元

#### フロントエンド
```bash
# 既存のアーカイブを確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "ls -lh ~/*.tar.gz"

# 古いバージョンに戻す
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down && \
     rm -rf ./* && \
     tar -xzf ~/aimee-fe-latest.tar.gz && \
     docker-compose up -d --build"
```

#### バックエンド
```bash
# 既存のアーカイブを確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "ls -lh ~/*.tar.gz"

# 古いバージョンに戻す
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down && \
     tar -xzf ~/aimee-be-app.tar.gz && \
     docker-compose up -d"
```

### 2. 緊急時の対応

#### 全サービス停止
```bash
# フロントエンド停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down"

# バックエンド停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down"
```

#### 全サービス再起動
```bash
# バックエンド起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose up -d"

# 30秒待機
sleep 30

# フロントエンド起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose up -d"
```

---

## 📝 デプロイチェックリスト

### デプロイ前
- [ ] ローカルで動作確認済み
- [ ] テストが全てパス
- [ ] `.env`ファイルの設定確認
- [ ] データベースマイグレーションの確認
- [ ] SSHキーの権限確認 (`chmod 400`)

### デプロイ中
- [ ] バックアップ取得
- [ ] サービス停止
- [ ] コード転送
- [ ] 設定ファイル確認
- [ ] コンテナビルド・起動

### デプロイ後
- [ ] コンテナ起動確認 (`docker ps`)
- [ ] ログ確認（エラーなし）
- [ ] ヘルスチェック成功
- [ ] API疎通確認
- [ ] フロントエンド動作確認
- [ ] 主要機能のテスト

---

## 🔐 セキュリティノート

### 認証情報の管理
- SSHキー（`~/.ssh/aimee-key.pem`）は安全に保管
- RDSパスワードは`.env`ファイルで管理
- 本番環境の認証情報はコミットしない

### アクセス制限
- EC2セキュリティグループで必要なポートのみ開放
- RDSはEC2からのアクセスのみ許可

---

## 📞 サポート

問題が発生した場合は、以下の情報を収集してください：

```bash
# 全コンテナの状態
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "docker ps -a"
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker ps -a"

# 最新のログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "docker logs aimee-frontend --tail=200"
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker logs aimee-be-api-1 --tail=200"

# システムリソース
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "free -h && df -h"
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "free -h && df -h"
```

---

**最終更新**: 2025-10-23
