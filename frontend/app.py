import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# バックエンドAPI連携
from src.utils.api_client import AIMEEAPIClient

# APIクライアント初期化
api_client = AIMEEAPIClient()

# ページ設定
st.set_page_config(
    page_title="AIMEE - 配置調整システム",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
    <style>
    /* メインコンテナのスタイリング */
    .main {
        padding: 1rem;
    }
    
    /* サイドバーのスタイリング */
    .css-1d391kg {
        background-color: #1a1a2e;
    }
    
    /* チャットメッセージのスタイリング */
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* メトリクスカードのスタイリング */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* アラートカードのスタイリング */
    .alert-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* ボタンの基本スタイリング */
    .stButton > button {
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        font-weight: bold;
        transition: all 0.2s;
        min-height: 38px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* タイトルのスタイリング */
    h1 {
        color: #1a1a2e;
        font-weight: 800;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #16213e;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #0f3460;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

# ボタンカラーの定義
COLORS = {
    "green": {
        "bg": "#22c55e",
        "hover": "#16a34a",
        "text": "white"
    },
    "red": {
        "bg": "#ef4444",
        "hover": "#dc2626",
        "text": "white"
    },
    "blue": {
        "bg": "#3b82f6",
        "hover": "#2563eb",
        "text": "white"
    },
    "purple": {
        "bg": "#667eea",
        "hover": "#5a52d5",
        "text": "white"
    }
}

def styled_button(label, key, color="green", on_click=None):
    """スタイル付きボタンを作成"""
    button_id = f"button_{key}"
    color_config = COLORS.get(color, COLORS["green"])
    
    # ボタン固有のスタイル
    st.markdown(f"""
    <style>
    #{button_id} {{
        background-color: {color_config["bg"]} !important;
        color: {color_config["text"]} !important;
    }}
    #{button_id}:hover {{
        background-color: {color_config["hover"]} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # ボタンにIDを付与
    button_html = f'<span id="{button_id}"></span>'
    st.markdown(button_html, unsafe_allow_html=True)
    
    return st.button(label, key=key, use_container_width=True)

def main():
    # ヘッダー部分
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# 配置調整システム")
    with col2:
        st.markdown(f"**{datetime.now().strftime('%Y-%m-%d %H:%M')}**")
    
    # サイドバー
    with st.sidebar:
        st.markdown("## 📊 システムステータス")
        
        # リアルタイムアラート
        st.markdown("### 🚨 アラート")
        alerts = get_alerts()
        if alerts:
            for alert in alerts:
                st.error(f"{alert['icon']} {alert['message']}")
        else:
            st.success("✅ すべて正常に稼働中")
        
        st.markdown("---")
        
        # クイックアクション
        st.markdown("### ⚡ クイックアクション")
        
        # サイドバー用のボタンスタイル
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #667eea !important;
            color: white !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background-color: #5a52d5 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 データ更新", use_container_width=True):
            with st.spinner("データ更新中..."):
                # 少し待機してから更新
                import time
                time.sleep(0.5)
            st.rerun()
        if st.button("📋 履歴確認", use_container_width=True):
            st.info("RealWorksで確認してください")
        
        st.markdown("---")
        
        # システム情報 (今後実装)
        # st.markdown("### ℹ️ システム情報")
        # st.metric("稼働率", "98.5%", "2.3%")
        # st.metric("処理済み案件", "1,234件", "156件")
    
    # メインコンテンツ - チャットのみに集中
    show_chat_interface()

def get_alerts():
    """アラート情報を取得（バックエンドAPIから実データ）"""
    try:
        # バックエンドAPIからアラート基準チェックを実行
        result = api_client.check_alerts()

        if "error" in result:
            # API接続エラー
            return [
                {"icon": "⚠️", "message": f"⚠️ API接続エラー: {result['error']}"}
            ]

        # APIからのアラートを整形
        alerts_data = []
        for alert in result.get("alerts", [])[:5]:  # 最大5件表示
            # アイコンは優先度に応じて設定
            if alert.get("priority") == "critical":
                icon = "🔴"
                color = "red"
            elif alert.get("priority") == "high":
                icon = "🟠"
                color = "orange"
            elif alert.get("priority") == "medium":
                icon = "🟡"
                color = "yellow"
            else:
                icon = "🟢"
                color = "green"

            # メッセージにアイコンを含めない
            alerts_data.append({
                "icon": icon,
                "message": alert.get("title", "アラート"),
                "id": alert.get("id"),
                "details": alert.get("message"),
                "priority": alert.get("priority"),
                "color": color
            })

        # アラートがない場合はDB状態を表示
        if not alerts_data:
            return [
                {"icon": "✅", "message": "✅ すべて正常に稼働中 (DBから取得)", "id": None}
            ]

        return alerts_data

    except Exception as e:
        # エラー時は接続エラーを表示
        return [
            {"icon": "⚠️", "message": f"⚠️ システムエラー: {str(e)}", "id": None}
        ]

def show_chat_interface():
    """チャットインターフェース"""
    
    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": """
こんにちは！AIMEEです。配置調整のお手伝いをします。

現在の状況をリアルタイムで分析し、最適な人員配置を提案します。
以下のようなご相談に対応できます：

• 特定工程の遅延への対応
• 人員不足の解消
• 効率的な配置の提案
• 過去の成功事例に基づく最適化

どのようなお手伝いが必要ですか？
            """}
        ]
    
    # 提案カード表示エリア
    suggestion_container = st.container()
    
    # チャット履歴表示
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # アシスタントのメッセージに提案が含まれる場合
                if message["role"] == "assistant" and "suggestion" in message:
                    show_suggestion_card(message["suggestion"])
    
    # チャット入力
    if prompt := st.chat_input("配置に関する相談を入力してください..."):
        # ユーザーメッセージを追加
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # ローディング表示を強化
        with chat_container:
            with st.chat_message("assistant"):
                # プログレス表示
                progress_placeholder = st.empty()

                with progress_placeholder:
                    st.info("分析中...")

                # AI応答を生成（バックエンドAPIを呼び出す）
                response, suggestion = generate_ai_response(prompt)

                # ローディング表示をクリア
                progress_placeholder.empty()

        # アシスタントメッセージを追加
        message_data = {"role": "assistant", "content": response}
        if suggestion:
            message_data["suggestion"] = suggestion

        st.session_state.messages.append(message_data)

        # 応答を再描画
        st.rerun()

def generate_ai_response(prompt):
    """AI応答を生成（バックエンドAPIから - 完全API連携）"""
    try:
        # バックエンドAPIでAI処理
        result = api_client.chat_with_ai(message=prompt, detail=False)

        if "error" in result:
            # エラー表示のみ - モックは使用しない
            error_msg = result.get("error", "不明なエラー")
            return f"❌ **バックエンドAPIエラー**\n\n{error_msg}\n\nバックエンドが起動しているか確認してください。", None

        # API応答を整形
        response = result.get("response", "応答を生成できませんでした")

        # 提案があれば整形 (changesが空でない場合のみ)
        suggestion = None
        if result.get("suggestion"):
            sug_data = result["suggestion"]
            changes = sug_data.get("changes", [])

            # changesが空でない、または明示的な配置転換が必要な場合のみ提案を表示
            if changes and len(changes) > 0:
                suggestion = {
                    "id": sug_data.get("id", "N/A"),
                    "changes": changes,
                    "impact": sug_data.get("impact", {}),
                    "reason": sug_data.get("reason", ""),
                    "rag_operators": result.get("rag_results", {}).get("recommended_operators", [])
                }

        return response, suggestion

    except Exception as e:
        # エラー表示のみ
        return f"❌ **システムエラー**\n\n{str(e)}\n\nバックエンドとの通信に失敗しました。", None



def show_suggestion_card(suggestion):
    """提案カードを表示"""
    with st.expander("📋 配置調整提案の詳細", expanded=True):
        # メッセージ表示用のプレースホルダー
        message_placeholder = st.empty()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔄 配置変更内容")
            for i, change in enumerate(suggestion["changes"]):
                # 配置変更を視覚的にわかりやすく表示
                st.markdown(f"""
                <div style="background: linear-gradient(to right, #f3f4f6, #e5e7eb); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 1;">
                            <span style="font-size: 1.1rem; font-weight: 600; color: #374151;">{change['from']}</span>
                            <br>
                            <span style="font-size: 0.9rem; color: #6b7280;">{change['process']}</span>
                        </div>
                        <div style="flex: 0.5; text-align: center;">
                            <span style="font-size: 1.5rem; color: #3b82f6;">→</span>
                            <br>
                            <span style="font-size: 2.2rem; font-weight: 700; color: #ef4444;">{change['count']}名</span>
                        </div>
                        <div style="flex: 1; text-align: right;">
                            <span style="font-size: 1.1rem; font-weight: 600; color: #374151;">{change['to']}</span>
                            <br>
                            <span style="font-size: 0.9rem; color: #6b7280;">{change['process']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### 📈 予測される効果")
            
            # 効果をカード形式で表示
            st.markdown(f"""
            <div style="background: #f0fdf4; border: 2px solid #22c55e; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <div style="text-align: center;">
                    <span style="font-size: 0.9rem; color: #166534;">生産性</span>
                    <br>
                    <span style="font-size: 2rem; font-weight: 700; color: #22c55e;">{suggestion["impact"]["productivity"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: #fef2f2; border: 2px solid #ef4444; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <div style="text-align: center;">
                    <span style="font-size: 0.9rem; color: #991b1b;">遅延解消</span>
                    <br>
                    <span style="font-size: 2rem; font-weight: 700; color: #ef4444;">{suggestion["impact"]["delay"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: #eff6ff; border: 2px solid #3b82f6; padding: 1rem; border-radius: 8px;">
                <div style="text-align: center;">
                    <span style="font-size: 0.9rem; color: #1e40af;">品質</span>
                    <br>
                    <span style="font-size: 1.5rem; font-weight: 700; color: #3b82f6;">{suggestion["impact"]["quality"]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.info(f"💡 {suggestion['reason']}")
        
        # カスタムボタンスタイル
        st.markdown(f"""
        <style>
        .suggestion-buttons-{suggestion['id']} {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}
        #{suggestion['id']}-approve {{
            background-color: #22c55e !important;
            color: white !important;
        }}
        #{suggestion['id']}-approve:hover {{
            background-color: #16a34a !important;
        }}
        #{suggestion['id']}-reject {{
            background-color: #ef4444 !important;
            color: white !important;
        }}
        #{suggestion['id']}-reject:hover {{
            background-color: #dc2626 !important;
        }}
        #{suggestion['id']}-discuss {{
            background-color: #3b82f6 !important;
            color: white !important;
        }}
        #{suggestion['id']}-discuss:hover {{
            background-color: #2563eb !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f'<span id="{suggestion["id"]}-approve"></span>', unsafe_allow_html=True)
            if st.button("✅ 承認", key=f"approve_{suggestion['id']}", use_container_width=True):
                # バックエンドAPIで承認実行
                result = api_client.execute_approval_action(
                    approval_id=suggestion['id'],
                    action="approve",
                    user="管理者",
                    user_id="admin001",
                    reason="チャットから承認",
                    notes=""
                )

                if result.get("success"):
                    message_placeholder.success("✅ 配置変更を承認しました")
                    send_notification(suggestion)
                else:
                    message_placeholder.error(f"❌ 承認に失敗しました: {result.get('error', '不明なエラー')}")

        with col2:
            st.markdown(f'<span id="{suggestion["id"]}-reject"></span>', unsafe_allow_html=True)
            if st.button("❌ 却下", key=f"reject_{suggestion['id']}", use_container_width=True):
                # バックエンドAPIで却下実行
                result = api_client.execute_approval_action(
                    approval_id=suggestion['id'],
                    action="reject",
                    user="管理者",
                    user_id="admin001",
                    reason="却下",
                    notes=""
                )

                if result.get("success"):
                    message_placeholder.info("❌ 配置変更を却下しました")
                else:
                    message_placeholder.error(f"❌ 却下に失敗しました: {result.get('error', '不明なエラー')}")

        with col3:
            st.markdown(f'<span id="{suggestion["id"]}-discuss"></span>', unsafe_allow_html=True)
            if st.button("💬 詳細を相談", key=f"discuss_{suggestion['id']}", use_container_width=True):
                message_placeholder.info("💬 詳細な相談モードに移行します")


if __name__ == "__main__":
    main()