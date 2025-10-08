#!/bin/bash

###############################################################################
# AIMEE システム状態確認スクリプト
# バックエンド、フロントエンド、DBの状態を確認します
###############################################################################

echo "🔍 AIMEE システム状態確認"
echo "========================================"
echo ""

# MySQL確認
echo "【1】MySQL"
if mysql.server status > /dev/null 2>&1; then
    echo "✅ MySQL: 起動中"
else
    echo "❌ MySQL: 停止中"
    echo "   起動するには: mysql.server start"
fi

# DB接続確認
echo ""
echo "【2】データベース接続"
python3 -c "
import sys
sys.path.append('/Users/umemiya/Desktop/erax/aimee-db')
try:
    from config import db_manager
    if db_manager.test_connection():
        print('✅ DB接続: 成功 (aimee_db)')
    else:
        print('❌ DB接続: 失敗')
except Exception as e:
    print(f'❌ DB接続エラー: {e}')
" 2>/dev/null || echo "❌ DB接続確認スクリプトエラー"

# バックエンド確認
echo ""
echo "【3】バックエンド (ポート 8002)"
if curl -s http://localhost:8002/api/v1/health > /dev/null 2>&1; then
    echo "✅ バックエンド: 起動中"
    echo "   API: http://localhost:8002/docs"

    # バージョン情報取得
    VERSION=$(curl -s http://localhost:8002/api/v1/health | python3 -c "import sys, json; print(json.load(sys.stdin).get('version', 'N/A'))" 2>/dev/null)
    echo "   バージョン: $VERSION"
else
    echo "❌ バックエンド: 停止中"
    echo "   起動するには: ./start_backend.sh"
fi

# フロントエンド確認
echo ""
echo "【4】フロントエンド (ポート 8501)"
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ フロントエンド: 起動中"
    echo "   アプリ: http://localhost:8501"
else
    echo "❌ フロントエンド: 停止中"
    echo "   起動するには: ./start_frontend.sh"
fi

# tmux/screenセッション確認
echo ""
echo "【5】セッション管理"
if command -v tmux &> /dev/null; then
    if tmux has-session -t aimee 2>/dev/null; then
        echo "✅ tmuxセッション 'aimee': アクティブ"
        echo "   アタッチ: tmux attach -t aimee"
    else
        echo "ℹ️  tmuxセッション 'aimee': なし"
    fi
fi

if command -v screen &> /dev/null; then
    BACKEND_SCREEN=$(screen -ls | grep "aimee-backend" | wc -l)
    FRONTEND_SCREEN=$(screen -ls | grep "aimee-frontend" | wc -l)

    if [ $BACKEND_SCREEN -gt 0 ]; then
        echo "✅ screenセッション 'aimee-backend': アクティブ"
    fi

    if [ $FRONTEND_SCREEN -gt 0 ]; then
        echo "✅ screenセッション 'aimee-frontend': アクティブ"
    fi
fi

# プロセス確認
echo ""
echo "【6】プロセス一覧"
echo "ポート8002 (バックエンド):"
lsof -ti:8002 > /dev/null 2>&1 && lsof -i:8002 | grep LISTEN || echo "   なし"

echo ""
echo "ポート8501 (フロントエンド):"
lsof -ti:8501 > /dev/null 2>&1 && lsof -i:8501 | grep LISTEN || echo "   なし"

echo ""
echo "========================================"
echo "🔗 クイックリンク"
echo "  - API文書: http://localhost:8002/docs"
echo "  - フロントエンド: http://localhost:8501"
echo ""
