#!/bin/bash

###############################################################################
# AIMEE フロントエンド起動スクリプト
# ポート: 8501 (Streamlitデフォルト)
# アプリURL: http://localhost:8501
###############################################################################

echo "🎨 AIMEE フロントエンドを起動します..."
echo ""

# フロントエンドディレクトリに移動
FRONTEND_DIR="/Users/umemiya/Desktop/erax/aimee-fe/frontend"
cd "$FRONTEND_DIR" || exit 1

# Pythonバージョン確認
echo "🐍 Pythonバージョン確認..."
python3 --version

# Streamlitインストール確認
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlitがインストールされていません"
    read -p "📦 Streamlitをインストールしますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install streamlit plotly pandas requests
    else
        echo "❌ Streamlitが必要です。手動でインストールしてください:"
        echo "   pip3 install streamlit plotly pandas requests"
        exit 1
    fi
fi

# バックエンド接続確認
echo ""
echo "🔌 バックエンド接続を確認中..."
if curl -s http://localhost:8002/api/v1/health > /dev/null 2>&1; then
    echo "✅ バックエンド接続: 成功"
else
    echo "⚠️  バックエンドが起動していません"
    echo "💡 別のターミナルでバックエンドを起動してください:"
    echo "   cd /Users/umemiya/Desktop/erax/aimee-fe"
    echo "   ./start_backend.sh"
    echo ""
    read -p "⏩ バックエンドなしで続行しますか? (モックデータで動作) (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Streamlit起動
echo ""
echo "🌐 Streamlitアプリを起動します..."
echo "📍 アプリ: http://localhost:8501"
echo ""
echo "🛑 停止するには: Ctrl+C"
echo ""

streamlit run app.py
