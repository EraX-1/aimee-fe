#!/bin/bash

###############################################################################
# AIMEE バックエンド Docker起動スクリプト
# docker-compose を使用してバックエンドを起動します
###############################################################################

echo "🐳 AIMEE バックエンドをDockerで起動します..."
echo ""

# バックエンドディレクトリに移動
BACKEND_DIR="/Users/umemiya/Desktop/erax/aimee-be"
cd "$BACKEND_DIR" || exit 1

# Docker起動確認
if ! docker info > /dev/null 2>&1; then
    echo "❌ Dockerが起動していません"
    echo "💡 Docker Desktopを起動してください"
    exit 1
fi

echo "✅ Docker起動確認: OK"
echo ""

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️  .envファイルが見つかりません"
    if [ -f ".env.example" ]; then
        echo "📄 .env.exampleからコピーしています..."
        cp .env.example .env
        echo "✅ .envファイルを作成しました"
    else
        echo "❌ .env.exampleも見つかりません"
        exit 1
    fi
fi

# docker-composeファイルの選択
COMPOSE_FILE="docker-compose.yml"

# Mac M3の場合は専用ファイルを使用するか確認
if [ -f "docker-compose-mac-m3.yml" ]; then
    echo "💡 Mac M3用のdocker-compose-mac-m3.ymlが見つかりました"
    read -p "🍎 Mac M3用の設定を使用しますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        COMPOSE_FILE="docker-compose-mac-m3.yml"
        echo "✅ Mac M3用の設定で起動します"
    fi
fi

echo "📦 使用するDocker Compose: $COMPOSE_FILE"
echo ""

# 既存のコンテナを停止
echo "🛑 既存のコンテナを停止中..."
docker-compose -f "$COMPOSE_FILE" down

# イメージのビルドとコンテナ起動
echo ""
echo "🔨 イメージをビルド中..."
docker-compose -f "$COMPOSE_FILE" build api

echo ""
echo "🚀 コンテナを起動中..."
docker-compose -f "$COMPOSE_FILE" up -d

# 起動確認
echo ""
echo "⏳ サービスの起動を待機中..."
sleep 5

# ヘルスチェック
echo ""
echo "🔍 サービス状態確認:"
docker-compose -f "$COMPOSE_FILE" ps

echo ""
echo "✅ バックエンドを起動しました"
echo ""
echo "📍 APIドキュメント: http://localhost:8002/docs"
echo "📊 ChromaDB: http://localhost:8002 (ポート競合注意)"
echo "💾 Redis: localhost:6380"
echo "🗄️  MySQL: localhost:3306"
echo ""
echo "🔍 ログ確認: docker-compose -f $COMPOSE_FILE logs -f api"
echo "🛑 停止: docker-compose -f $COMPOSE_FILE down"
echo ""
