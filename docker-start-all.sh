#!/bin/bash

###############################################################################
# AIMEE 全体 Docker起動スクリプト
# バックエンドとフロントエンドをDockerで起動します
###############################################################################

echo "🐳 AIMEE システム全体をDockerで起動します..."
echo ""

# スクリプトのディレクトリ取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="/Users/umemiya/Desktop/erax/aimee-be"

# Docker起動確認
if ! docker info > /dev/null 2>&1; then
    echo "❌ Dockerが起動していません"
    echo ""
    echo "💡 Docker Desktopを起動してください"
    echo "   アプリケーション > Docker を起動"
    echo ""
    exit 1
fi

echo "✅ Docker起動確認: OK"
echo ""

# 実行権限確認
if [ ! -x "$SCRIPT_DIR/docker-start-backend.sh" ] || [ ! -x "$SCRIPT_DIR/docker-start-frontend.sh" ]; then
    echo "📝 起動スクリプトに実行権限を付与します..."
    chmod +x "$SCRIPT_DIR/docker-start-backend.sh"
    chmod +x "$SCRIPT_DIR/docker-start-frontend.sh"
    echo "✅ 実行権限を付与しました"
    echo ""
fi

# バックエンドを起動
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "【1/2】バックエンド起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$BACKEND_DIR" || exit 1

# docker-composeファイルの選択
BACKEND_COMPOSE_FILE="docker-compose.yml"

# 既存のコンテナを停止
echo "🛑 既存のバックエンドコンテナを停止中..."
docker-compose -f "$BACKEND_COMPOSE_FILE" down

# バックエンドをバックグラウンドで起動
echo ""
echo "🔨 バックエンドイメージをビルド中..."
docker-compose -f "$BACKEND_COMPOSE_FILE" build api

echo ""
echo "🚀 バックエンドコンテナを起動中..."
docker-compose -f "$BACKEND_COMPOSE_FILE" up -d

echo ""
echo "⏳ バックエンドの起動を待機中..."
sleep 10

# バックエンドヘルスチェック
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8002/api/v1/health > /dev/null 2>&1; then
        echo "✅ バックエンド起動完了"
        break
    fi
    echo "⏳ バックエンド起動待機中... ($((RETRY_COUNT+1))/$MAX_RETRIES)"
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT+1))
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ バックエンドの起動に失敗しました"
    echo "💡 ログを確認してください:"
    echo "   cd $BACKEND_DIR"
    echo "   docker-compose -f $BACKEND_COMPOSE_FILE logs api"
    exit 1
fi

# フロントエンドを起動
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "【2/2】フロントエンド起動"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$SCRIPT_DIR" || exit 1

# 既存のコンテナを停止
echo "🛑 既存のフロントエンドコンテナを停止中..."
docker-compose down

# フロントエンドをバックグラウンドで起動
echo ""
echo "🔨 フロントエンドイメージをビルド中..."
docker-compose build

echo ""
echo "🚀 フロントエンドコンテナを起動中..."
docker-compose up -d

echo ""
echo "⏳ フロントエンドの起動を待機中..."
sleep 8

# 全体の状態確認
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 システム状態確認"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "【バックエンド】"
cd "$BACKEND_DIR"
docker-compose -f "$BACKEND_COMPOSE_FILE" ps | grep -E "(api|mysql|redis|chromadb)"

echo ""
echo "【フロントエンド】"
cd "$SCRIPT_DIR"
docker-compose ps

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ システム起動完了!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 フロントエンド: http://localhost:8501"
echo "📍 バックエンドAPI: http://localhost:8002/docs"
echo "📊 ChromaDB: http://localhost:8002 (注意: APIとポート共有)"
echo "💾 Redis: localhost:6380"
echo "🗄️  MySQL: localhost:3306"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 便利コマンド"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 ログ確認:"
echo "  バックエンド: cd $BACKEND_DIR && docker-compose logs -f api"
echo "  フロントエンド: cd $SCRIPT_DIR && docker-compose logs -f frontend"
echo ""
echo "🛑 停止:"
echo "  全体: ./docker-stop-all.sh"
echo "  バックエンドのみ: cd $BACKEND_DIR && docker-compose down"
echo "  フロントエンドのみ: cd $SCRIPT_DIR && docker-compose down"
echo ""
echo "🔄 再起動:"
echo "  ./docker-start-all.sh"
echo ""
