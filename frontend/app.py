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
    
    # URLクエリパラメータからデバッグモード取得
    query_params = st.query_params
    debug_mode = query_params.get("debug") == "1"

    # session_stateにデバッグモード保存
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = debug_mode

    # セッションIDの初期化
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = f"session_{uuid.uuid4().hex[:12]}"

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

                # デバッグ情報表示（デバッグモードON時のみ）
                if message["role"] == "assistant" and "debug_info" in message and message["debug_info"]:
                    show_debug_info(message["debug_info"])
    
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
                response, suggestion, debug_info = generate_ai_response(prompt)

                # ローディング表示をクリア
                progress_placeholder.empty()

        # アシスタントメッセージを追加
        message_data = {"role": "assistant", "content": response}
        if suggestion:
            message_data["suggestion"] = suggestion
        if debug_info:
            message_data["debug_info"] = debug_info

        st.session_state.messages.append(message_data)

        # 応答を再描画
        st.rerun()

def generate_ai_response(prompt):
    """AI応答を生成（バックエンドAPIから - 完全API連携）"""
    try:
        # セッションIDを取得
        session_id = st.session_state.get("session_id", "default")

        # バックエンドAPIでAI処理
        result = api_client.chat_with_ai(
            message=prompt,
            session_id=session_id,
            debug=st.session_state.get("debug_mode", False)
        )

        if "error" in result:
            # エラー表示のみ - モックは使用しない
            error_msg = result.get("error", "不明なエラー")
            return f"❌ **バックエンドAPIエラー**\n\n{error_msg}\n\nバックエンドが起動しているか確認してください。", None, None

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

        # デバッグ情報を取得
        debug_info = result.get("debug_info") if st.session_state.get("debug_mode", False) else None

        return response, suggestion, debug_info

    except Exception as e:
        # エラー表示のみ
        return f"❌ **システムエラー**\n\n{str(e)}\n\nバックエンドとの通信に失敗しました。", None, None



def show_suggestion_card(suggestion):
    """提案カードを表示（各提案ごとに個別のexpanderと承認ボタン）"""

    # 全体サマリー
    total_people = sum(c.get('count', 0) for c in suggestion['changes'])
    total_changes = len(suggestion['changes'])

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
        <h3 style="margin: 0; color: white;">📋 配置調整提案</h3>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem;">合計 {total_changes}件の提案（移動人数: {total_people}人）</p>
    </div>
    """, unsafe_allow_html=True)

    # 各提案ごとに個別のexpanderを作成
    for i, change in enumerate(suggestion["changes"], 1):
        # 4階層情報を取得
        from_cat = change.get('from_business_category', 'N/A')
        from_biz = change.get('from_business_name', 'N/A')
        from_ocr = change.get('from_process_category', '')
        from_proc = change.get('from_process_name', 'N/A')

        to_cat = change.get('to_business_category', 'N/A')
        to_biz = change.get('to_business_name', 'N/A')
        to_ocr = change.get('to_process_category', '')
        to_proc = change.get('to_process_name', 'N/A')

        # 4階層表示文字列を作成
        from_text = f"{from_cat} > {from_biz}"
        if from_ocr:
            from_text += f" > {from_ocr}"
        from_text += f" > {from_proc}"

        to_text = f"{to_cat} > {to_biz}"
        if to_ocr:
            to_text += f" > {to_ocr}"
        to_text += f" > {to_proc}"

        count = change.get('count', 0)
        operators = change.get('operators', [])

        # 提案タイトル
        expander_title = f"提案{i}: {from_cat} → {to_cat} ({from_proc}, {count}人)"

        # 各提案ごとにexpander作成
        with st.expander(expander_title, expanded=(i == 1)):  # 最初だけ展開
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("#### 🔄 配置変更内容")

                # 配置変更を視覚的にわかりやすく表示
                st.markdown(f"""
                <div style="background: linear-gradient(to right, #f3f4f6, #e5e7eb); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 1;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: #374151;">{from_text}</span>
                        </div>
                        <div style="flex: 0.3; text-align: center;">
                            <span style="font-size: 1.5rem; color: #3b82f6;">→</span>
                            <br>
                            <span style="font-size: 1.8rem; font-weight: 700; color: #ef4444;">{count}名</span>
                        </div>
                        <div style="flex: 1; text-align: right;">
                            <span style="font-size: 0.85rem; font-weight: 600; color: #374151;">{to_text}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # オペレータ名を表示
                if operators and len(operators) > 0:
                    st.markdown("**👥 対象オペレータ:**")
                    for operator in operators:
                        st.markdown(f"• {operator}")
                else:
                    st.markdown("*オペレータ未選定*")

            with col2:
                st.markdown("#### 📈 効果")

                # 効果を簡潔に表示
                st.markdown(f"""
                <div style="background: #f0fdf4; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.3rem; text-align: center;">
                    <span style="font-size: 0.8rem; color: #166534;">生産性</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #22c55e;"> +10%</span>
                </div>
                <div style="background: #fef2f2; padding: 0.5rem; border-radius: 4px; margin-bottom: 0.3rem; text-align: center;">
                    <span style="font-size: 0.8rem; color: #991b1b;">遅延</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #ef4444;"> -15分</span>
                </div>
                <div style="background: #eff6ff; padding: 0.5rem; border-radius: 4px; text-align: center;">
                    <span style="font-size: 0.8rem; color: #1e40af;">品質</span>
                    <span style="font-size: 1.2rem; font-weight: 700; color: #3b82f6;"> 維持</span>
                </div>
                """, unsafe_allow_html=True)

            # 承認済み・却下済みの状態を管理（各changeごと）
            approval_key = f"approval_status_{suggestion['id']}_change_{i}"
            if approval_key not in st.session_state:
                st.session_state[approval_key] = None

            # 処理済みの場合はステータスを表示
            if st.session_state[approval_key] == "approved":
                st.success("✅ この提案は承認済みです")
            elif st.session_state[approval_key] == "rejected":
                st.warning("❌ この提案は却下済みです")

            # 承認/却下ボタン（各changeごと）
            col1, col2, col3 = st.columns([1, 1, 1])
            is_processed = st.session_state[approval_key] is not None

            with col1:
                if st.button("✅ 承認", key=f"approve_{suggestion['id']}_change_{i}", use_container_width=True, disabled=is_processed):
                    # バックエンドAPIで承認実行
                    with st.spinner("承認処理中..."):
                        # 1件の変更だけを承認するためのsuggestionを作成
                        single_change_suggestion = {
                            "id": f"{suggestion['id']}_change_{i}",
                            "changes": [change],
                            "impact": suggestion.get("impact", {}),
                            "reason": f"提案{i}を個別承認",
                            "confidence_score": suggestion.get("confidence_score", 0.85)
                        }

                        result = api_client.execute_approval_action(
                            approval_id=single_change_suggestion['id'],
                            action="approve",
                            user="管理者",
                            user_id="admin001",
                            reason=f"提案{i}をチャットから承認",
                            notes=""
                        )

                    if result.get("success"):
                        st.success(f"✅ 提案{i}を承認しました")
                        st.session_state[approval_key] = "approved"
                        st.rerun()
                    else:
                        st.error(f"❌ 承認失敗: {result.get('error', '不明なエラー')}")

            with col2:
                if st.button("❌ 却下", key=f"reject_{suggestion['id']}_change_{i}", use_container_width=True, disabled=is_processed):
                    # バックエンドAPIで却下実行
                    with st.spinner("却下処理中..."):
                        single_change_suggestion = {
                            "id": f"{suggestion['id']}_change_{i}",
                            "changes": [change],
                            "impact": suggestion.get("impact", {}),
                            "reason": f"提案{i}を個別却下",
                            "confidence_score": suggestion.get("confidence_score", 0.85)
                        }

                        result = api_client.execute_approval_action(
                            approval_id=single_change_suggestion['id'],
                            action="reject",
                            user="管理者",
                            user_id="admin001",
                            reason=f"提案{i}をチャットから却下",
                            notes=""
                        )

                    if result.get("success"):
                        st.warning(f"❌ 提案{i}を却下しました")
                        st.session_state[approval_key] = "rejected"
                        st.rerun()
                    else:
                        st.error(f"❌ 却下失敗: {result.get('error', '不明なエラー')}")

            with col3:
                if st.button("💬 相談", key=f"discuss_{suggestion['id']}_change_{i}", use_container_width=True):
                    st.info(f"💬 提案{i}の詳細相談モード")


def show_debug_info(debug_info):
    """デバッグ情報を表示"""
    with st.expander("🔍 デバッグ情報（開発者向け）", expanded=False):

        # 1. 意図解析
        if debug_info.get("intent_analysis"):
            st.subheader("1️⃣ 意図解析")
            intent = debug_info["intent_analysis"]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Intent Type", intent.get("raw_intent", {}).get("intent_type", "N/A"))
            with col2:
                st.metric("Location", intent.get("extracted_location", "N/A"))
            with col3:
                st.metric("Process", intent.get("extracted_process", "N/A"))

            # expanderの代わりにst.json()を直接使用
            st.write("**詳細JSON:**")
            st.json(intent)

        # 2. RAG検索結果
        if debug_info.get("rag_results"):
            st.subheader("2️⃣ RAG検索結果")
            rag = debug_info["rag_results"]

            st.write(f"**検索結果数**: {rag.get('manager_rules_count', 0)}件")

            if rag.get("manager_rules"):
                for i, rule in enumerate(rag["manager_rules"], 1):
                    st.markdown(f"**ルール{i}**: {rule.get('title', 'N/A')} (類似度: {rule.get('similarity', 0):.3f})")
                    st.write(f"カテゴリ: {rule.get('category', 'N/A')}")
                    st.code(rule.get('rule_text', '')[:200], language=None)

        # 3. データベースクエリ
        if debug_info.get("database_queries"):
            st.subheader("3️⃣ データベースクエリ")
            db_queries = debug_info["database_queries"]

            col1, col2 = st.columns(2)
            with col1:
                st.metric("実行クエリ数", len(db_queries.get("executed_queries", [])))
            with col2:
                st.metric("総レコード数", db_queries.get("total_records", 0))

            # SQL文を表示
            if db_queries.get("executed_queries"):
                for i, query_info in enumerate(db_queries["executed_queries"], 1):
                    st.markdown(f"**SQL {i}** ({query_info.get('intent_type', 'N/A')})")
                    st.code(query_info.get("sql", "")[:500], language="sql")
                    if query_info.get("params"):
                        st.write("パラメータ:", query_info["params"])
                    st.markdown("---")

        # 4. スキルマッチング詳細
        if debug_info.get("skill_matching"):
            st.subheader("4️⃣ スキルマッチング詳細")
            st.json(debug_info["skill_matching"])

        # 5. 処理時間
        if debug_info.get("processing_time"):
            st.subheader("5️⃣ 処理時間内訳")
            st.json(debug_info["processing_time"])


if __name__ == "__main__":
    main()