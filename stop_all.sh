#!/bin/bash

###############################################################################
# AIMEE 全体停止スクリプト
# バックエンドとフロントエンドを停止します
###############################################################################

echo "🛑 AIMEE システムを停止します..."
echo ""

# tmuxセッション停止
if command -v tmux &> /dev/null; then
    if tmux has-session -t aimee 2>/dev/null; then
        echo "📺 tmuxセッション 'aimee' を終了します..."
        tmux kill-session -t aimee
        echo "✅ tmuxセッションを終了しました"
    fi
fi

# screenセッション停止
if command -v screen &> /dev/null; then
    if screen -ls | grep -q "aimee-backend"; then
        echo "📺 screenセッション 'aimee-backend' を終了します..."
        screen -X -S aimee-backend quit
        echo "✅ バックエンドを停止しました"
    fi

    if screen -ls | grep -q "aimee-frontend"; then
        echo "📺 screenセッション 'aimee-frontend' を終了します..."
        screen -X -S aimee-frontend quit
        echo "✅ フロントエンドを停止しました"
    fi
fi

# ポート8002で動作しているプロセスを停止
echo ""
echo "🔍 ポート8002で動作しているプロセスを確認中..."
PID=$(lsof -ti:8002)
if [ ! -z "$PID" ]; then
    echo "🛑 ポート8002のプロセス(PID: $PID)を停止します..."
    kill -9 $PID 2>/dev/null
    echo "✅ バックエンドプロセスを停止しました"
else
    echo "ℹ️  ポート8002で動作しているプロセスはありません"
fi

# ポート8501で動作しているプロセスを停止 (Streamlit)
echo ""
echo "🔍 ポート8501で動作しているプロセスを確認中..."
PID=$(lsof -ti:8501)
if [ ! -z "$PID" ]; then
    echo "🛑 ポート8501のプロセス(PID: $PID)を停止します..."
    kill -9 $PID 2>/dev/null
    echo "✅ フロントエンドプロセスを停止しました"
else
    echo "ℹ️  ポート8501で動作しているプロセスはありません"
fi

echo ""
echo "✅ システムを停止しました"
