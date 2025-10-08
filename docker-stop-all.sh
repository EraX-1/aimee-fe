#!/bin/bash

###############################################################################
# AIMEE 全体 Docker停止スクリプト
# バックエンドとフロントエンドのDockerコンテナを停止します
###############################################################################

echo "🛑 AIMEE Dockerコンテナを停止します..."
echo ""

BACKEND_DIR="/Users/umemiya/Desktop/erax/aimee-be"
FRONTEND_DIR="/Users/umemiya/Desktop/erax/aimee-fe"

# フロントエンド停止
echo "【1/2】フロントエンド停止中..."
cd "$FRONTEND_DIR" || exit 1
docker-compose down
echo "✅ フロントエンド停止完了"

echo ""

# バックエンド停止
echo "【2/2】バックエンド停止中..."
cd "$BACKEND_DIR" || exit 1

# docker-composeファイルの確認
if [ -f "docker-compose-mac-m3.yml" ]; then
    # 両方試す
    docker-compose -f docker-compose.yml down 2>/dev/null
    docker-compose -f docker-compose-mac-m3.yml down 2>/dev/null
else
    docker-compose down
fi

echo "✅ バックエンド停止完了"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ すべてのコンテナを停止しました"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 コンテナとボリュームを完全削除するには:"
echo "   cd $BACKEND_DIR && docker-compose down -v"
echo "   cd $FRONTEND_DIR && docker-compose down -v"
echo ""
