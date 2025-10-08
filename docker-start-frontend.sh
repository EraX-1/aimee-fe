#!/bin/bash

###############################################################################
# AIMEE フロントエンド Docker起動スクリプト
# docker-compose を使用してフロントエンドを起動します
###############################################################################

echo "🐳 AIMEE フロントエンドをDockerで起動します..."
echo ""

# フロントエンドディレクトリに移動
FRONTEND_DIR="/Users/umemiya/Desktop/erax/aimee-fe"
cd "$FRONTEND_DIR" || exit 1

# Docker起動確認
if ! docker info > /dev/null 2>&1; then
    echo "❌ Dockerが起動していません"
    echo "💡 Docker Desktopを起動してください"
    exit 1
fi

echo "✅ Docker起動確認: OK"
echo ""

# バックエンド起動確認
echo "🔌 バックエンド接続を確認中..."
if curl -s http://localhost:8002/api/v1/health > /dev/null 2>&1; then
    echo "✅ バックエンド起動確認: OK"
else
    echo "⚠️  バックエンドが起動していません"
    echo ""
    echo "💡 バックエンドを先に起動してください:"
    echo "   cd /Users/umemiya/Desktop/erax/aimee-fe"
    echo "   ./docker-start-backend.sh"
    echo ""
    read -p "⏩ バックエンドなしで続行しますか? (モックデータで動作) (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 既存のコンテナを停止
echo ""
echo "🛑 既存のコンテナを停止中..."
docker-compose down

# イメージのビルドとコンテナ起動
echo ""
echo "🔨 イメージをビルド中..."
docker-compose build

echo ""
echo "🚀 コンテナを起動中..."
docker-compose up -d

# 起動確認
echo ""
echo "⏳ Streamlitの起動を待機中..."
sleep 8

# ヘルスチェック
echo ""
echo "🔍 サービス状態確認:"
docker-compose ps

echo ""
echo "✅ フロントエンドを起動しました"
echo ""
echo "📍 アプリURL: http://localhost:8501"
echo "🔗 バックエンドAPI: http://localhost:8002"
echo ""
echo "🔍 ログ確認: docker-compose logs -f frontend"
echo "🛑 停止: docker-compose down"
echo ""
