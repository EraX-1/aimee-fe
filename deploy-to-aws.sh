#!/bin/bash

#########################################
# AIMEE AWS デプロイスクリプト
#
# 使用方法:
#   ./deploy-to-aws.sh          # 全体デプロイ
#   ./deploy-to-aws.sh frontend # フロントエンドのみ
#   ./deploy-to-aws.sh backend  # バックエンドのみ
#
# 注意: 初回実行前に改行コードを修正:
#   sed -i '' 's/\r$//' deploy-to-aws.sh
#   chmod +x deploy-to-aws.sh
#########################################

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 設定
SSH_KEY="$HOME/.ssh/aimee-key.pem"
FRONTEND_IP="43.207.175.35"
BACKEND_IP="54.150.242.233"
SSH_USER="ubuntu"
RDS_ENDPOINT="aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306"

# ヘルパー関数
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# SSH接続確認
check_ssh_connection() {
    print_header "SSH接続確認"

    # SSHキー権限確認
    if [ ! -f "$SSH_KEY" ]; then
        print_error "SSHキーが見つかりません: $SSH_KEY"
        exit 1
    fi

    chmod 400 "$SSH_KEY" 2>/dev/null
    print_success "SSHキー権限: 400"

    # フロントエンド接続確認
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SSH_USER@$FRONTEND_IP" "echo 'OK'" > /dev/null 2>&1; then
        print_success "フロントエンドサーバー接続OK ($FRONTEND_IP)"
    else
        print_error "フロントエンドサーバーに接続できません"
        exit 1
    fi

    # バックエンド接続確認
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SSH_USER@$BACKEND_IP" "echo 'OK'" > /dev/null 2>&1; then
        print_success "バックエンドサーバー接続OK ($BACKEND_IP)"
    else
        print_error "バックエンドサーバーに接続できません"
        exit 1
    fi
}

# フロントエンドデプロイ
deploy_frontend() {
    print_header "フロントエンドデプロイ"

    # アーカイブ作成
    print_info "アーカイブ作成中..."
    tar --exclude='node_modules' \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='*.tar.gz' \
        -czf /tmp/aimee-fe-deploy.tar.gz . 2>/dev/null

    SIZE=$(ls -lh /tmp/aimee-fe-deploy.tar.gz | awk '{print $5}')
    print_success "アーカイブ作成完了 ($SIZE)"

    # EC2に転送
    print_info "EC2に転送中..."
    scp -i "$SSH_KEY" /tmp/aimee-fe-deploy.tar.gz "$SSH_USER@$FRONTEND_IP:~/aimee-fe-new.tar.gz" > /dev/null 2>&1
    print_success "転送完了"

    # 既存コンテナ停止
    print_info "既存コンテナ停止中..."
    ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "cd ~/aimee-fe && docker-compose down" 2>&1 | grep -q "done" || true
    print_success "コンテナ停止完了"

    # 新コード展開
    print_info "新しいコード展開中..."
    ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "cd ~/aimee-fe && rm -rf * && tar -xzf ~/aimee-fe-new.tar.gz" 2>&1 | grep -v "Ignoring unknown" > /dev/null
    print_success "コード展開完了"

    # docker-compose.yml更新（プラットフォームをamd64に設定）
    print_info "docker-compose.yml設定中..."
    ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "cd ~/aimee-fe && cat > docker-compose.yml << 'EOFDC'
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
      - AIMEE_API_URL=http://$BACKEND_IP:8002
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_HEADLESS=true
      - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    restart: unless-stopped
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8501/_stcore/health\"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

networks:
  default:
    driver: bridge
EOFDC
"
    print_success "設定ファイル更新完了"

    # ビルド・起動
    print_info "コンテナビルド・起動中（3-5分かかります）..."
    ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "cd ~/aimee-fe && docker-compose up -d --build" 2>&1 | tail -5

    # 起動待機
    sleep 15

    # 起動確認
    if ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "docker ps | grep -q aimee-frontend"; then
        print_success "フロントエンド起動完了"

        # アクセス確認
        if curl -s "http://$FRONTEND_IP:8501" | grep -q "Streamlit"; then
            print_success "フロントエンド動作確認OK"
            echo -e "\n${GREEN}🌐 フロントエンドURL: http://$FRONTEND_IP:8501${NC}"
        else
            print_error "フロントエンドにアクセスできません"
        fi
    else
        print_error "コンテナが起動していません"
        ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "docker logs aimee-frontend --tail=20"
        exit 1
    fi
}

# バックエンドデプロイ
deploy_backend() {
    print_header "バックエンドデプロイ"

    # カレントディレクトリ確認
    if [ ! -d "/Users/umemiya/Desktop/erax/aimee-be" ]; then
        print_error "aimee-beディレクトリが見つかりません"
        exit 1
    fi

    # アーカイブ作成
    print_info "アーカイブ作成中..."
    cd /Users/umemiya/Desktop/erax/aimee-be
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
        app Dockerfile.api docker-compose.yml .env start.py requirements.txt 2>/dev/null

    SIZE=$(ls -lh /tmp/aimee-be-deploy.tar.gz | awk '{print $5}')
    print_success "アーカイブ作成完了 ($SIZE)"

    cd /Users/umemiya/Desktop/erax/aimee-fe

    # EC2に転送
    print_info "EC2に転送中..."
    scp -i "$SSH_KEY" /tmp/aimee-be-deploy.tar.gz "$SSH_USER@$BACKEND_IP:~/aimee-be-new.tar.gz" > /dev/null 2>&1
    print_success "転送完了"

    # 既存コンテナ停止
    print_info "既存コンテナ停止中..."
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "cd ~/aimee-be && docker-compose down" 2>&1 | grep -q "Removed" || true
    print_success "コンテナ停止完了"

    # 新コード展開
    print_info "新しいコード展開中..."
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "cd ~/aimee-be && tar -xzf ~/aimee-be-new.tar.gz" 2>&1 | grep -v "Ignoring unknown" > /dev/null
    print_success "コード展開完了"

    # .env修正（RDS接続）
    print_info ".env設定中（RDS接続）..."
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "cd ~/aimee-be && sed -i 's|DATABASE_URL=.*|DATABASE_URL=mysql+aiomysql://admin:Aimee2024!RDS@$RDS_ENDPOINT/aimee_db|' .env"
    print_success ".env更新完了（RDS接続）"

    # docker-compose.yml修正（プラットフォーム、DATABASE_URL）
    print_info "docker-compose.yml設定中..."
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "cd ~/aimee-be && sed -i 's|platform: linux/arm64/v8|platform: linux/amd64|g' docker-compose.yml"
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "cd ~/aimee-be && sed -i 's|DATABASE_URL:.*|DATABASE_URL: mysql+aiomysql://admin:Aimee2024!RDS@$RDS_ENDPOINT/aimee_db|' docker-compose.yml"
    print_success "docker-compose.yml更新完了"

    # コンテナ起動
    print_info "コンテナ起動中（5-10分かかります）..."
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "cd ~/aimee-be && docker-compose up -d" 2>&1 | tail -10

    # 起動待機
    print_info "起動待機中（30秒）..."
    sleep 30

    # 起動確認
    if ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "docker ps | grep -q aimee-be-api"; then
        print_success "バックエンド起動完了"

        # ヘルスチェック
        if curl -s "http://$BACKEND_IP:8002/api/v1/health" | grep -q "healthy"; then
            print_success "API動作確認OK"
            echo -e "\n${GREEN}🌐 バックエンドURL: http://$BACKEND_IP:8002${NC}"
        else
            print_error "APIが応答していません"
        fi
    else
        print_error "コンテナが起動していません"
        ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "docker ps -a | grep aimee-be"
        exit 1
    fi
}

# 動作確認テスト
test_deployment() {
    print_header "動作確認テスト"

    # APIテスト
    print_info "スキルベースマッチングテスト実行中..."

    RESPONSE=$(curl -s -X POST "http://$BACKEND_IP:8002/api/v1/chat/message" \
        -H "Content-Type: application/json" \
        -d '{"message":"SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。","context":{},"session_id":"deploy_test"}' \
        --max-time 120)

    if echo "$RESPONSE" | grep -q "suggestion"; then
        print_success "APIテスト成功"

        # 提案内容を確認
        CHANGE_COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('suggestion', {}).get('changes', [])))" 2>/dev/null || echo "0")

        if [ "$CHANGE_COUNT" -gt 0 ]; then
            print_success "配置提案生成: ${CHANGE_COUNT}件"

            # 異なる工程間移動を確認
            HAS_CROSS_PROCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); c=d.get('suggestion', {}).get('changes', []); print('yes' if c and c[0].get('from_process_name') != c[0].get('to_process_name') else 'no')" 2>/dev/null || echo "no")

            if [ "$HAS_CROSS_PROCESS" = "yes" ]; then
                print_success "異なる工程間移動: 正常動作"
            fi
        fi
    else
        print_error "APIが正しく応答していません"
        echo "$RESPONSE" | head -50
    fi

    # フロントエンドアクセス確認
    print_info "フロントエンドアクセステスト..."
    if curl -s "http://$FRONTEND_IP:8501" | grep -q "Streamlit"; then
        print_success "フロントエンドアクセスOK"
    else
        print_error "フロントエンドにアクセスできません"
    fi
}

# サマリー表示
show_summary() {
    print_header "デプロイ完了サマリー"

    echo -e "${GREEN}【フロントエンド】${NC}"
    echo -e "  URL: http://$FRONTEND_IP:8501"

    # コンテナ状態
    FE_STATUS=$(ssh -i "$SSH_KEY" "$SSH_USER@$FRONTEND_IP" "docker ps --format '{{.Status}}' --filter name=aimee-frontend" 2>/dev/null || echo "不明")
    echo -e "  状態: $FE_STATUS"

    echo -e "\n${GREEN}【バックエンド】${NC}"
    echo -e "  URL: http://$BACKEND_IP:8002"
    echo -e "  API Docs: http://$BACKEND_IP:8002/docs"

    # コンテナ状態
    BE_STATUS=$(ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "docker ps --format '{{.Status}}' --filter name=aimee-be-api" 2>/dev/null || echo "不明")
    echo -e "  状態: $BE_STATUS"

    echo -e "\n${GREEN}【サービス一覧】${NC}"
    ssh -i "$SSH_KEY" "$SSH_USER@$BACKEND_IP" "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep aimee-be" 2>/dev/null || true

    echo -e "\n${YELLOW}【確認方法】${NC}"
    echo -e "  1. ブラウザで http://$FRONTEND_IP:8501 にアクセス"
    echo -e "  2. チャット画面で配置相談を入力"
    echo -e "  3. スキルベースマッチング（異なる工程間移動）を確認"
}

# メイン処理
main() {
    cd /Users/umemiya/Desktop/erax/aimee-fe

    MODE="${1:-all}"

    case $MODE in
        frontend)
            print_header "フロントエンドのみデプロイ"
            check_ssh_connection
            deploy_frontend
            test_deployment
            show_summary
            ;;
        backend)
            print_header "バックエンドのみデプロイ"
            check_ssh_connection
            deploy_backend
            test_deployment
            show_summary
            ;;
        all|*)
            print_header "AIMEE 全体デプロイ開始"
            check_ssh_connection
            deploy_frontend
            deploy_backend
            test_deployment
            show_summary
            ;;
    esac

    print_success "デプロイ完了！"
}

# スクリプト実行
main "$@"
