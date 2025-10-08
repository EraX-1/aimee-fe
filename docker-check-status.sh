#!/bin/bash

###############################################################################
# AIMEE Docker システム状態確認スクリプト
###############################################################################

echo "🔍 AIMEE Docker システム状態確認"
echo "========================================"
echo ""

BACKEND_DIR="/Users/umemiya/Desktop/erax/aimee-be"
FRONTEND_DIR="/Users/umemiya/Desktop/erax/aimee-fe"

# Docker確認
echo "【1】Docker"
if docker info > /dev/null 2>&1; then
    echo "✅ Docker: 起動中"
    DOCKER_VERSION=$(docker version --format '{{.Server.Version}}' 2>/dev/null)
    echo "   バージョン: $DOCKER_VERSION"
else
    echo "❌ Docker: 停止中"
    echo "   起動するには: Docker Desktopを起動"
    exit 1
fi

# バックエンドコンテナ確認
echo ""
echo "【2】バックエンドコンテナ"
cd "$BACKEND_DIR" || exit 1

BACKEND_RUNNING=$(docker-compose ps -q api 2>/dev/null | wc -l)

if [ "$BACKEND_RUNNING" -gt 0 ]; then
    echo "✅ バックエンドコンテナ: 起動中"
    docker-compose ps | grep -E "(api|mysql|redis|chromadb|ollama)" | head -10

    # API接続確認
    if curl -s http://localhost:8002/api/v1/health > /dev/null 2>&1; then
        echo ""
        echo "   ✅ API接続: 成功"
        echo "   📍 http://localhost:8002/docs"
    else
        echo ""
        echo "   ⚠️  API接続: 失敗 (起動中の可能性)"
    fi
else
    echo "❌ バックエンドコンテナ: 停止中"
    echo "   起動するには: ./docker-start-backend.sh"
fi

# フロントエンドコンテナ確認
echo ""
echo "【3】フロントエンドコンテナ"
cd "$FRONTEND_DIR" || exit 1

FRONTEND_RUNNING=$(docker-compose ps -q frontend 2>/dev/null | wc -l)

if [ "$FRONTEND_RUNNING" -gt 0 ]; then
    echo "✅ フロントエンドコンテナ: 起動中"
    docker-compose ps

    # Streamlit接続確認
    if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        echo ""
        echo "   ✅ Streamlit接続: 成功"
        echo "   📍 http://localhost:8501"
    else
        echo ""
        echo "   ⚠️  Streamlit接続: 失敗 (起動中の可能性)"
    fi
else
    echo "❌ フロントエンドコンテナ: 停止中"
    echo "   起動するには: ./docker-start-frontend.sh"
fi

# ボリューム確認
echo ""
echo "【4】Dockerボリューム"
echo "使用中のボリューム:"
docker volume ls | grep -E "(aimee|mysql|chroma|redis|ollama)" || echo "   なし"

# ネットワーク確認
echo ""
echo "【5】Dockerネットワーク"
echo "使用中のネットワーク:"
docker network ls | grep -E "(aimee|backend|frontend)" || echo "   デフォルトブリッジのみ"

# ポート確認
echo ""
echo "【6】ポート使用状況"
echo "8002 (バックエンドAPI):"
lsof -i:8002 2>/dev/null | grep LISTEN || echo "   未使用"

echo ""
echo "8501 (フロントエンド):"
lsof -i:8501 2>/dev/null | grep LISTEN || echo "   未使用"

echo ""
echo "3306 (MySQL):"
lsof -i:3306 2>/dev/null | grep LISTEN || echo "   未使用"

echo ""
echo "========================================"
echo "🔗 クイックリンク"
echo "  - フロントエンド: http://localhost:8501"
echo "  - API文書: http://localhost:8002/docs"
echo ""
echo "💡 便利コマンド"
echo "  - 全体起動: ./docker-start-all.sh"
echo "  - 全体停止: ./docker-stop-all.sh"
echo "  - ログ確認:"
echo "    cd $BACKEND_DIR && docker-compose logs -f api"
echo "    cd $FRONTEND_DIR && docker-compose logs -f frontend"
echo ""
