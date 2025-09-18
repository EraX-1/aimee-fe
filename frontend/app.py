import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
        st.markdown("# 🤖 AIMEE - AI配置最適化システム")
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
            st.rerun()
        if st.button("📋 履歴確認", use_container_width=True):
            st.info("RealWorksで確認してください")
        
        st.markdown("---")
        
        # システム情報
        st.markdown("### ℹ️ システム情報")
        st.metric("稼働率", "98.5%", "2.3%")
        st.metric("処理済み案件", "1,234件", "156件")
    
    # メインコンテンツ
    tab1, tab2 = st.tabs(["💬 配置調整アシスタント", "✅ 配置承認"])
    
    with tab1:
        show_chat_interface()
    
    with tab2:
        show_approval_interface()

def get_alerts():
    """アラート情報を取得"""
    # 実際の実装では、バックエンドAPIから取得
    return [
        {"icon": "🔴", "message": "札幌エントリ1工程で遅延発生中"},
        {"icon": "🟡", "message": "品川で15分後に人員不足予測"}
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
        
        # AI応答を生成（実際の実装ではAPIを呼び出す）
        response, suggestion = generate_ai_response(prompt)
        
        # アシスタントメッセージを追加
        message_data = {"role": "assistant", "content": response}
        if suggestion:
            message_data["suggestion"] = suggestion
        
        st.session_state.messages.append(message_data)
        
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(response)
                if suggestion:
                    show_suggestion_card(suggestion)

def generate_ai_response(prompt):
    """AI応答を生成（モック）"""
    # 実際の実装では、LLMやRAGを使用
    
    # デモ用の応答
    response = f"""
了解しました。「{prompt}」について分析します。

📊 **現在の状況分析：**
- 札幌エントリ1工程: 処理遅延 20分
- 現在配置: 12名
- 処理残: 450件
- 必要処理能力: 550件/時

🎯 **最適化提案：**
以下の配置調整を提案します：
"""
    
    suggestion = {
        "id": "SGT2024-001",
        "changes": [
            {"from": "盛岡", "to": "札幌", "process": "エントリ1", "count": 3},
            {"from": "品川", "to": "札幌", "process": "エントリ1", "count": 2},
            {"from": "西梅田", "to": "札幌", "process": "エントリ1", "count": 1}
        ],
        "impact": {
            "productivity": "+25%",
            "delay": "-30分",
            "quality": "維持"
        },
        "reason": "過去の類似ケースでは、この配置により95%の確率で遅延解消"
    }
    
    return response, suggestion

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
                message_placeholder.success("✅ 配置変更を承認しました")
                send_notification(suggestion)
        with col2:
            st.markdown(f'<span id="{suggestion["id"]}-reject"></span>', unsafe_allow_html=True)
            if st.button("❌ 却下", key=f"reject_{suggestion['id']}", use_container_width=True):
                message_placeholder.info("❌ 配置変更を却下しました")
        with col3:
            st.markdown(f'<span id="{suggestion["id"]}-discuss"></span>', unsafe_allow_html=True)
            if st.button("💬 詳細を相談", key=f"discuss_{suggestion['id']}", use_container_width=True):
                message_placeholder.info("💬 詳細な相談モードに移行します")

def show_approval_interface():
    """配置承認インターフェース"""
    st.markdown("## 承認待ちの配置変更")
    
    # メッセージ表示用のプレースホルダー（共通の場所）
    message_placeholder = st.empty()
    
    # 承認待ちリスト（実際の実装ではAPIから取得）
    pending_approvals = get_pending_approvals()
    
    if not pending_approvals:
        st.info("現在、承認待ちの配置変更はありません")
        return
    
    for approval in pending_approvals:
        with st.container():
            # カード風のスタイリング
            st.markdown(f"""
            <div style="background: #f0f2f6; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
                <h3 style="color: #1a1a2e; margin-bottom: 1rem;">
                    提案ID: {approval['id']} - {approval['timestamp']}
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # 配置変更の可視化
                show_allocation_visualization(approval)
            
            with col2:
                st.markdown("### 📊 影響予測")
                st.metric("処理能力", f"+{approval['impact']['capacity']}件/時")
                st.metric("遅延リスク", approval['impact']['delay_risk'], 
                         delta=f"{approval['impact']['delay_change']}")
                st.metric("品質スコア", approval['impact']['quality'])
                
                st.markdown("---")
                
                # 承認ページ用のボタンスタイル
                st.markdown(f"""
                <style>
                #batch-{approval['id']}-approve {{
                    background-color: #22c55e !important;
                    color: white !important;
                }}
                #batch-{approval['id']}-approve:hover {{
                    background-color: #16a34a !important;
                }}
                #batch-{approval['id']}-reject {{
                    background-color: #ef4444 !important;
                    color: white !important;
                }}
                #batch-{approval['id']}-reject:hover {{
                    background-color: #dc2626 !important;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f'<span id="batch-{approval["id"]}-approve"></span>', unsafe_allow_html=True)
                if st.button("✅ 一括承認",
                           key=f"batch_approve_{approval['id']}", 
                           use_container_width=True):
                    message_placeholder.success(f"✅ 提案 {approval['id']} を承認しました")
                    send_notification(approval)
                
                st.markdown(f'<span id="batch-{approval["id"]}-reject"></span>', unsafe_allow_html=True)
                if st.button("❌ 却下", key=f"batch_reject_{approval['id']}", 
                           use_container_width=True):
                    message_placeholder.info(f"❌ 提案 {approval['id']} を却下しました")

def get_pending_approvals():
    """承認待ちの配置変更を取得（モック）"""
    return [
        {
            "id": "APV2024-001",
            "timestamp": "2024-01-15 10:30",
            "changes": [
                {"from": "札幌", "to": "盛岡", "process": "エントリ2", "count": 3},
                {"from": "品川", "to": "札幌", "process": "エントリ1", "count": 2}
            ],
            "impact": {
                "capacity": 230,
                "delay_risk": "低",
                "delay_change": "-15%",
                "quality": "98.5%"
            },
            "urgency": "high"
        }
    ]

def show_allocation_visualization(approval):
    """配置変更の可視化"""
    # 業務別の人員配置をヒートマップで表示
    locations = ["札幌", "盛岡", "品川", "西梅田", "本町東", "沖縄"]
    processes = ["エントリ1", "エントリ2", "補正", "SV補正"]
    
    # ダミーデータ（実際はAPIから取得）
    current_data = pd.DataFrame({
        "札幌": [12, 8, 6, 3],
        "盛岡": [8, 5, 4, 2],
        "品川": [15, 10, 8, 4],
        "西梅田": [10, 8, 5, 3],
        "本町東": [8, 6, 4, 2],
        "沖縄": [6, 4, 3, 2]
    }, index=processes)
    
    # ヒートマップ作成
    fig = go.Figure(data=go.Heatmap(
        z=current_data.values,
        x=locations,
        y=processes,
        colorscale='Blues',
        text=current_data.values,
        texttemplate="%{text}名",
        textfont={"size": 12},
        hovertemplate="拠点: %{x}<br>工程: %{y}<br>人数: %{text}名<extra></extra>"
    ))
    
    # 変更箇所をハイライト
    for change in approval["changes"]:
        # 実装では変更箇所に矢印やマーカーを追加
        pass
    
    fig.update_layout(
        title="配置変更の可視化",
        height=300,
        xaxis_title="拠点",
        yaxis_title="工程",
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def send_notification(data):
    """通知を送信（モック）"""
    # 実際の実装では、WebSocketやAPIを使用して通知を送信
    st.toast(f"✅ 配置変更が承認されました: {data.get('id', 'N/A')}", icon="✅")

if __name__ == "__main__":
    main()