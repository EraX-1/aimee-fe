#!/bin/bash

###############################################################################
# AIMEE バックエンド起動スクリプト
# ポート: 8002
# APIドキュメント: http://localhost:8002/docs
###############################################################################

echo "🚀 AIMEE バックエンドを起動します..."
echo ""

# バックエンドディレクトリに移動
BACKEND_DIR="/Users/umemiya/Desktop/erax/aimee-be"
cd "$BACKEND_DIR" || exit 1

# .envファイルの確認
if [ ! -f ".env" ]; then
    echo "⚠️  .envファイルが見つかりません"
    if [ -f ".env.example" ]; then
        echo "📄 .env.exampleからコピーしています..."
        cp .env.example .env
        echo "✅ .envファイルを作成しました"
    else
        echo "❌ .env.exampleも見つかりません。手動で.envを作成してください"
        exit 1
    fi
fi

# Pythonバージョン確認
echo "🐍 Pythonバージョン確認..."
python3 --version

# 依存関係の確認 (初回のみ実行を推奨)
read -p "📚 依存関係をインストールしますか? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 依存関係をインストール中..."
    pip3 install -r requirements.txt
fi

# DB接続確認
echo ""
echo "🔌 データベース接続を確認中..."
python3 -c "
import sys
sys.path.append('/Users/umemiya/Desktop/erax/aimee-db')
from config import db_manager
if db_manager.test_connection():
    print('✅ データベース接続: 成功')
else:
    print('❌ データベース接続: 失敗')
    print('⚠️  MySQLが起動しているか確認してください')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "💡 MySQLを起動するには:"
    echo "   mysql.server start"
    echo ""
    exit 1
fi

# サーバー起動
echo ""
echo "🌐 FastAPIサーバーを起動します..."
echo "📍 API: http://localhost:8002"
echo "📖 ドキュメント: http://localhost:8002/docs"
echo ""
echo "🛑 停止するには: Ctrl+C"
echo ""

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
