#!/bin/bash

###############################################################################
# AIMEE 全体起動スクリプト
# バックエンドとフロントエンドを同時に起動します
###############################################################################

echo "🚀 AIMEE システム全体を起動します..."
echo ""

# スクリプトのディレクトリ取得
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 実行権限確認
if [ ! -x "$SCRIPT_DIR/start_backend.sh" ] || [ ! -x "$SCRIPT_DIR/start_frontend.sh" ]; then
    echo "📝 起動スクリプトに実行権限を付与します..."
    chmod +x "$SCRIPT_DIR/start_backend.sh"
    chmod +x "$SCRIPT_DIR/start_frontend.sh"
    echo "✅ 実行権限を付与しました"
    echo ""
fi

# MySQL起動確認
echo "🔌 MySQL接続を確認中..."
if ! mysql.server status > /dev/null 2>&1; then
    echo "⚠️  MySQLが起動していません"
    read -p "🔧 MySQLを起動しますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔧 MySQLを起動中..."
        mysql.server start
        sleep 2
    else
        echo "❌ MySQLが必要です。手動で起動してください:"
        echo "   mysql.server start"
        exit 1
    fi
fi

# tmux または screen の確認
if command -v tmux &> /dev/null; then
    SESSION_NAME="aimee"

    echo "📺 tmuxセッション '$SESSION_NAME' を作成します..."
    echo ""

    # 既存セッションを削除
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null

    # 新しいセッションを作成してバックエンドを起動
    tmux new-session -d -s "$SESSION_NAME" -n "backend" "cd '$SCRIPT_DIR' && ./start_backend.sh"

    # フロントエンド用のウィンドウを作成
    tmux new-window -t "$SESSION_NAME:1" -n "frontend" "cd '$SCRIPT_DIR' && sleep 5 && ./start_frontend.sh"

    echo "✅ バックエンドとフロントエンドを起動しました"
    echo ""
    echo "📍 バックエンドAPI: http://localhost:8002/docs"
    echo "📍 フロントエンド: http://localhost:8501"
    echo ""
    echo "💡 tmuxセッションにアタッチするには:"
    echo "   tmux attach -t $SESSION_NAME"
    echo ""
    echo "💡 ウィンドウ切り替え: Ctrl+B → 0 (backend) / 1 (frontend)"
    echo "💡 セッション終了: tmux kill-session -t $SESSION_NAME"
    echo ""

elif command -v screen &> /dev/null; then
    echo "📺 screenでバックエンドとフロントエンドを起動します..."

    # バックエンドをバックグラウンドで起動
    screen -dmS aimee-backend bash -c "cd '$SCRIPT_DIR' && ./start_backend.sh"
    sleep 5

    # フロントエンドをバックグラウンドで起動
    screen -dmS aimee-frontend bash -c "cd '$SCRIPT_DIR' && ./start_frontend.sh"

    echo "✅ バックエンドとフロントエンドを起動しました"
    echo ""
    echo "📍 バックエンドAPI: http://localhost:8002/docs"
    echo "📍 フロントエンド: http://localhost:8501"
    echo ""
    echo "💡 screenセッション確認:"
    echo "   screen -ls"
    echo ""
    echo "💡 セッション終了:"
    echo "   screen -X -S aimee-backend quit"
    echo "   screen -X -S aimee-frontend quit"
    echo ""

else
    echo "⚠️  tmux または screen がインストールされていません"
    echo ""
    echo "💡 別々のターミナルで起動してください:"
    echo ""
    echo "【ターミナル1】バックエンド:"
    echo "   cd $SCRIPT_DIR"
    echo "   ./start_backend.sh"
    echo ""
    echo "【ターミナル2】フロントエンド:"
    echo "   cd $SCRIPT_DIR"
    echo "   ./start_frontend.sh"
    echo ""

    read -p "📺 tmuxをインストールしますか? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v brew &> /dev/null; then
            echo "📦 Homebrewでtmuxをインストール中..."
            brew install tmux
            echo "✅ tmuxをインストールしました。再度このスクリプトを実行してください"
        else
            echo "💡 Homebrewがインストールされていません"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        fi
    fi
fi
