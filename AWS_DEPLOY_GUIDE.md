# AIMEE AWS デプロイガイド

## 📋 目次
1. [デプロイ方法の選択肢](#デプロイ方法の選択肢)
2. [推奨構成: AWS ECS (Fargate)](#推奨構成-aws-ecs-fargate)
3. [代替案: EC2 + Docker Compose](#代替案-ec2--docker-compose)
4. [コスト試算](#コスト試算)
5. [ステップバイステップ手順](#ステップバイステップ手順)

---

## デプロイ方法の選択肢

### 🎯 推奨: AWS ECS (Fargate) ⭐
**特徴**:
- サーバー管理不要 (フルマネージド)
- 自動スケーリング
- ヘルスチェック・ロールバック自動
- コンテナ単位での管理

**向いているケース**:
- AWS運用経験がある
- 長期運用を見据えている
- 自動スケーリングが必要

**月額コスト**: 約¥40,000〜¥80,000

---

### 💰 コスパ重視: EC2 + Docker Compose
**特徴**:
- シンプル構成
- 現在のローカル環境と同じ
- 初期セットアップが簡単
- コスト予測しやすい

**向いているケース**:
- デモ・PoC目的
- 短期間の運用 (数週間〜数ヶ月)
- AWS初心者

**月額コスト**: 約¥25,000〜¥60,000 (インスタンスタイプによる)

---

### ⚡ 最安: AWS Lambda + API Gateway (制限あり)
**特徴**:
- 使った分だけ課金
- サーバーレス

**制限**:
- OllamaなどのLLMが動作しない
- コールドスタート問題
- 実行時間制限 (最大15分)

**結論**: AIMEEには不向き ❌

---

## 推奨構成: AWS ECS (Fargate)

### システム構成図

```
Internet
   │
   ▼
[ALB: Application Load Balancer]
   │
   ├─────▶ [ECS Service: Frontend (Streamlit)]  Port 8501
   │
   └─────▶ [ECS Service: Backend (FastAPI)]     Port 8002
              │
              ├─────▶ [ECS Task: Ollama Light]    Port 11433
              ├─────▶ [ECS Task: Ollama Main]     Port 11435
              ├─────▶ [ECS Task: ChromaDB]        Port 8003
              ├─────▶ [ECS Task: Redis]           Port 6380
              │
              ▼
         [RDS MySQL 8.0]                          Port 3306
```

### 必要なAWSサービス

1. **ECS (Elastic Container Service)**: コンテナオーケストレーション
2. **Fargate**: サーバーレスコンテナ実行環境
3. **ECR (Elastic Container Registry)**: Dockerイメージ保存
4. **RDS MySQL**: データベース
5. **ALB (Application Load Balancer)**: ロードバランサー
6. **VPC**: ネットワーク
7. **CloudWatch**: ログ・監視
8. **Secrets Manager**: 認証情報管理
9. **EFS (Elastic File System)**: Ollamaモデル永続化用

---

## 代替案: EC2 + Docker Compose

### システム構成図

```
Internet
   │
   ▼
[EC2 Instance: t3.xlarge or g5.xlarge]
   │
   ├─ Docker: Frontend (Streamlit)      Port 8501
   ├─ Docker: Backend (FastAPI)         Port 8002
   ├─ Docker: Ollama Light              Port 11433
   ├─ Docker: Ollama Main               Port 11435
   ├─ Docker: ChromaDB                  Port 8003
   ├─ Docker: Redis                     Port 6380
   └─ MySQL (ローカル)                   Port 3306
```

### 必要なAWSリソース

1. **EC2 Instance**:
   - CPU負荷高い場合: `c6i.2xlarge` (8vCPU, 16GB RAM)
   - GPU必要な場合: `g5.xlarge` (4vCPU, 16GB RAM, NVIDIA A10G)
   - バランス型: `t3.xlarge` (4vCPU, 16GB RAM)

2. **Elastic IP**: 固定IPアドレス
3. **Security Group**: ファイアウォール
4. **EBS Volume**: ディスク (100GB以上推奨)

---

## コスト試算

### パターンA: ECS (Fargate) 構成

| リソース | スペック | 月額コスト (USD) | 月額コスト (JPY) |
|---------|---------|----------------|----------------|
| **Fargate (Frontend)** | 0.5 vCPU, 1GB RAM | $15 | ¥2,250 |
| **Fargate (Backend API)** | 2 vCPU, 4GB RAM | $60 | ¥9,000 |
| **Fargate (Ollama Light)** | 2 vCPU, 4GB RAM | $60 | ¥9,000 |
| **Fargate (Ollama Main)** | 4 vCPU, 8GB RAM | $120 | ¥18,000 |
| **Fargate (ChromaDB)** | 1 vCPU, 2GB RAM | $30 | ¥4,500 |
| **Fargate (Redis)** | 1 vCPU, 2GB RAM | $30 | ¥4,500 |
| **RDS MySQL (db.t3.medium)** | 2 vCPU, 4GB RAM | $65 | ¥9,750 |
| **ALB** | - | $25 | ¥3,750 |
| **EFS (Ollama models)** | 50GB | $15 | ¥2,250 |
| **データ転送** | 100GB/月 | $10 | ¥1,500 |
| **CloudWatch Logs** | 10GB/月 | $5 | ¥750 |
| **合計** | - | **$435** | **¥65,250** |

※ 1USD = 150円で計算

---

### パターンB: EC2 + Docker Compose 構成

#### オプション1: CPU型インスタンス (t3.xlarge)

| リソース | スペック | 月額コスト (USD) | 月額コスト (JPY) |
|---------|---------|----------------|----------------|
| **EC2 (t3.xlarge)** | 4 vCPU, 16GB RAM | $152 | ¥22,800 |
| **EBS (100GB gp3)** | 100GB SSD | $8 | ¥1,200 |
| **Elastic IP** | 固定IP | $3.6 | ¥540 |
| **データ転送** | 100GB/月 | $10 | ¥1,500 |
| **CloudWatch監視** | - | $3 | ¥450 |
| **合計** | - | **$176.6** | **¥26,490** |

**特徴**:
- 最安構成
- Ollama処理が遅い (10〜30秒)
- デモ・PoC向け

---

#### オプション2: GPU型インスタンス (g5.xlarge)

| リソース | スペック | 月額コスト (USD) | 月額コスト (JPY) |
|---------|---------|----------------|----------------|
| **EC2 (g5.xlarge)** | 4 vCPU, 16GB RAM, NVIDIA A10G | $505 | ¥75,750 |
| **EBS (100GB gp3)** | 100GB SSD | $8 | ¥1,200 |
| **Elastic IP** | 固定IP | $3.6 | ¥540 |
| **データ転送** | 100GB/月 | $10 | ¥1,500 |
| **CloudWatch監視** | - | $3 | ¥450 |
| **合計** | - | **$529.6** | **¥79,440** |

**特徴**:
- AI推論が高速 (1〜3秒)
- 本番運用レベル
- コスト高

---

#### オプション3: バランス型インスタンス (c6i.2xlarge)

| リソース | スペック | 月額コスト (USD) | 月額コスト (JPY) |
|---------|---------|----------------|----------------|
| **EC2 (c6i.2xlarge)** | 8 vCPU, 16GB RAM | $248 | ¥37,200 |
| **EBS (100GB gp3)** | 100GB SSD | $8 | ¥1,200 |
| **Elastic IP** | 固定IP | $3.6 | ¥540 |
| **データ転送** | 100GB/月 | $10 | ¥1,500 |
| **CloudWatch監視** | - | $3 | ¥450 |
| **合計** | - | **$272.6** | **¥40,890** |

**特徴**:
- CPU性能高い
- Ollama処理が快適 (5〜10秒)
- コスパ良好 ⭐推奨

---

### コスト比較まとめ

| 構成 | 月額コスト | AI応答速度 | 運用難易度 | 推奨用途 |
|------|----------|----------|----------|---------|
| **ECS (Fargate)** | ¥65,250 | 普通 (5〜10秒) | 高 | 長期運用・本番環境 |
| **EC2: t3.xlarge** | ¥26,490 | 遅い (10〜30秒) | 低 | デモ・PoC ⭐コスパ最強 |
| **EC2: c6i.2xlarge** | ¥40,890 | 快適 (5〜10秒) | 低 | 短〜中期運用 ⭐推奨 |
| **EC2: g5.xlarge** | ¥79,440 | 高速 (1〜3秒) | 低 | 高性能必要時 |

---

## ステップバイステップ手順

### 🚀 方法1: EC2 + Docker Compose (推奨: 初心者向け)

#### 事前準備

1. **AWS CLIインストール**
```bash
brew install awscli
aws configure
# Access Key ID: (AWSから取得)
# Secret Access Key: (AWSから取得)
# Region: ap-northeast-1 (東京)
```

2. **SSH鍵ペア作成**
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aimee-aws-key
chmod 400 ~/.ssh/aimee-aws-key
```

---

#### ステップ1: EC2インスタンス作成

```bash
# セキュリティグループ作成
aws ec2 create-security-group \
  --group-name aimee-sg \
  --description "AIMEE Security Group" \
  --vpc-id vpc-xxxxxxxxx  # VPC IDを指定

# インバウンドルール追加
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp --port 22 --cidr 0.0.0.0/0  # SSH

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp --port 8501 --cidr 0.0.0.0/0  # Streamlit

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp --port 8002 --cidr 0.0.0.0/0  # FastAPI

# EC2インスタンス起動 (c6i.2xlarge推奨)
aws ec2 run-instances \
  --image-id ami-0bba69335379e17f8 \  # Amazon Linux 2023 (東京リージョン)
  --instance-type c6i.2xlarge \
  --key-name aimee-aws-key \
  --security-group-ids sg-xxxxxxxxx \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=aimee-production}]'
```

---

#### ステップ2: EC2にSSH接続してセットアップ

```bash
# Elastic IP取得
INSTANCE_ID=i-xxxxxxxxx  # 上記で作成したインスタンスID
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id $INSTANCE_ID --allocation-id eipalloc-xxxxxxxxx

# SSH接続
PUBLIC_IP=xxx.xxx.xxx.xxx  # Elastic IPアドレス
ssh -i ~/.ssh/aimee-aws-key ec2-user@$PUBLIC_IP
```

---

#### ステップ3: EC2上でDockerセットアップ

```bash
# Docker インストール
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Docker Compose インストール
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 再ログイン (グループ反映)
exit
ssh -i ~/.ssh/aimee-aws-key ec2-user@$PUBLIC_IP
```

---

#### ステップ4: プロジェクトファイルをEC2にアップロード

**ローカルマシンで実行**:

```bash
# aimee-fe, aimee-be, aimee-db をまとめてアップロード
cd /Users/umemiya/Desktop/erax

# tar圧縮
tar czf aimee-deploy.tar.gz \
  aimee-fe/ \
  aimee-be/ \
  aimee-db/

# EC2にアップロード
scp -i ~/.ssh/aimee-aws-key aimee-deploy.tar.gz ec2-user@$PUBLIC_IP:~/

# SSH接続して展開
ssh -i ~/.ssh/aimee-aws-key ec2-user@$PUBLIC_IP
cd ~
tar xzf aimee-deploy.tar.gz
```

---

#### ステップ5: MySQL初期化

```bash
cd ~/aimee-db

# MySQLコンテナを単独起動してDB作成
docker run -d \
  --name aimee-mysql \
  -e MYSQL_ROOT_PASSWORD=root_password \
  -e MYSQL_DATABASE=aimee_db \
  -e MYSQL_USER=aimee_user \
  -e MYSQL_PASSWORD=Aimee2024! \
  -p 3306:3306 \
  -v ~/aimee-db:/docker-entrypoint-initdb.d:ro \
  mysql:8.0

# 初期化完了を待つ (約30秒)
sleep 30

# approval_history テーブル作成
docker exec -i aimee-mysql mysql -u aimee_user -p'Aimee2024!' aimee_db < approval_history_table.sql
```

---

#### ステップ6: バックエンド起動

```bash
cd ~/aimee-be

# .envファイル修正 (DBホストをlocalhostに変更)
cat > .env << 'EOF'
APP_NAME=AIMEE-Backend
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8002
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@host.docker.internal:3306/aimee_db
OLLAMA_LIGHT_HOST=ollama-light
OLLAMA_MAIN_HOST=ollama-main
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
REDIS_URL=redis://redis:6379/0
EOF

# Docker Compose起動
docker-compose up -d

# ログ確認
docker-compose logs -f
```

---

#### ステップ7: フロントエンド起動

```bash
cd ~/aimee-fe

# フロントエンドのdocker-compose.ymlを修正
# AIMEE_API_URLを EC2のパブリックIPに変更
cat > docker-compose.yml << EOF
version: '3.9'

services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: aimee-frontend
    ports:
      - "8501:8501"
    environment:
      - AIMEE_API_URL=http://$PUBLIC_IP:8002
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF

# Docker Compose起動
docker-compose up -d

# ログ確認
docker-compose logs -f
```

---

#### ステップ8: 動作確認

```bash
# バックエンドAPI確認
curl http://$PUBLIC_IP:8002/api/v1/health

# フロントエンド確認
curl http://$PUBLIC_IP:8501
```

**ブラウザでアクセス**:
- フロントエンド: `http://$PUBLIC_IP:8501`
- バックエンドAPI: `http://$PUBLIC_IP:8002/docs`

---

### 🎯 方法2: AWS ECS (Fargate) デプロイ (上級者向け)

#### 事前準備

1. **ECRリポジトリ作成**
```bash
# フロントエンド用
aws ecr create-repository --repository-name aimee-frontend

# バックエンド用
aws ecr create-repository --repository-name aimee-backend
```

2. **Dockerイメージビルド&プッシュ**
```bash
# ECRログイン
aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com

# バックエンドビルド
cd /Users/umemiya/Desktop/erax/aimee-be
docker build -f Dockerfile.api -t aimee-backend:latest .
docker tag aimee-backend:latest 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/aimee-backend:latest
docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/aimee-backend:latest

# フロントエンドビルド
cd /Users/umemiya/Desktop/erax/aimee-fe
docker build -t aimee-frontend:latest .
docker tag aimee-frontend:latest 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/aimee-frontend:latest
docker push 123456789012.dkr.ecr.ap-northeast-1.amazonaws.com/aimee-frontend:latest
```

3. **RDS MySQL作成**
```bash
aws rds create-db-instance \
  --db-instance-identifier aimee-db \
  --db-instance-class db.t3.medium \
  --engine mysql \
  --engine-version 8.0.35 \
  --master-username admin \
  --master-user-password YourSecurePassword123! \
  --allocated-storage 100 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --publicly-accessible
```

4. **ECS クラスター作成**
```bash
aws ecs create-cluster --cluster-name aimee-cluster
```

5. **タスク定義作成**

`task-definition.json` を作成 (内容は長いため省略、必要に応じて提供)

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

6. **ECSサービス作成**
```bash
aws ecs create-service \
  --cluster aimee-cluster \
  --service-name aimee-backend \
  --task-definition aimee-backend:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}"
```

---

## 🔐 セキュリティ設定

### 1. HTTPSを有効化 (Let's Encrypt)

```bash
# Nginxコンテナを追加
docker run -d \
  --name nginx-proxy \
  -p 80:80 \
  -p 443:443 \
  -v ~/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v ~/certs:/etc/letsencrypt:ro \
  nginx:alpine

# Certbot でSSL証明書取得
docker run -it --rm \
  -v ~/certs:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone \
  -d your-domain.com
```

### 2. ファイアウォール設定

```bash
# セキュリティグループでポート制限
# 本番環境では以下のみ公開:
# - 80 (HTTP)
# - 443 (HTTPS)
# - 22 (SSH: 管理者IPのみ)
```

---

## 📊 監視・ログ設定

### CloudWatch Logs設定

```bash
# Docker Compose に logging 設定を追加
services:
  api:
    logging:
      driver: awslogs
      options:
        awslogs-region: ap-northeast-1
        awslogs-group: /ecs/aimee-backend
        awslogs-stream-prefix: ecs
```

---

## 🛠️ トラブルシューティング

### EC2のメモリ不足

```bash
# スワップファイル作成 (8GB)
sudo dd if=/dev/zero of=/swapfile bs=1M count=8192
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Ollama モデルが起動しない

```bash
# モデルを手動ダウンロード
docker exec -it aimee-be-ollama-light-1 ollama pull qwen2:0.5b
docker exec -it aimee-be-ollama-main-1 ollama pull gemma3:4b
```

---

## ✅ チェックリスト

### デプロイ前
- [ ] AWSアカウント作成・招待確認
- [ ] AWS CLI設定完了
- [ ] SSH鍵ペア作成
- [ ] コスト上限設定 (Budgets)

### デプロイ中
- [ ] EC2インスタンス起動
- [ ] Elastic IP割り当て
- [ ] セキュリティグループ設定
- [ ] Docker / Docker Compose インストール
- [ ] プロジェクトファイルアップロード
- [ ] MySQL初期化
- [ ] バックエンド起動確認
- [ ] フロントエンド起動確認

### デプロイ後
- [ ] ブラウザでアクセス確認
- [ ] API動作確認
- [ ] ログ確認
- [ ] CloudWatch監視設定
- [ ] バックアップ設定
- [ ] HTTPSサポート (オプション)

---

## 📞 サポート

問題が発生した場合は以下を確認:

1. **EC2ログ確認**
```bash
docker-compose logs -f api
docker-compose logs -f frontend
```

2. **システムリソース確認**
```bash
docker stats
free -h
df -h
```

3. **ポート疎通確認**
```bash
curl http://localhost:8002/api/v1/health
curl http://localhost:8501
```

---

**作成日**: 2025-10-09
**最終更新**: デプロイガイド初版
