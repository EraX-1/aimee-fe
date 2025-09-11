import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="協会けんぽ 人員配置最適化システム",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🏢 協会けんぽ 人員配置最適化システム")
    
    with st.sidebar:
        st.header("ナビゲーション")
        st.markdown("---")
        
        menu_items = {
            "🏠 ホーム": "home",
            "👥 全体配置画面": "allocation",
            "📊 リアルタイム監視": "monitoring",
            "💬 配置調整チャット": "chat",
            "📈 分析レポート": "analytics",
            "⚙️ 設定": "settings"
        }
        
        selected_page = st.radio(
            "ページを選択",
            list(menu_items.keys()),
            index=0
        )
        
        st.markdown("---")
        st.caption(f"最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if menu_items[selected_page] == "home":
        show_home_page()
    elif menu_items[selected_page] == "allocation":
        show_allocation_page()
    elif menu_items[selected_page] == "monitoring":
        show_monitoring_page()
    elif menu_items[selected_page] == "chat":
        show_chat_page()
    elif menu_items[selected_page] == "analytics":
        show_analytics_page()
    elif menu_items[selected_page] == "settings":
        show_settings_page()

def show_home_page():
    st.header("ダッシュボード")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="総オペレータ数",
            value="156名",
            delta="12名"
        )
    
    with col2:
        st.metric(
            label="稼働率",
            value="87.5%",
            delta="2.3%"
        )
    
    with col3:
        st.metric(
            label="平均生産性",
            value="3,910件/日",
            delta="-120件"
        )
    
    with col4:
        st.metric(
            label="納期遵守率",
            value="98.5%",
            delta="0.5%"
        )
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔔 アラート")
        alerts = [
            {"level": "🔴", "message": "札幌拠点でエントリ1工程が遅延中"},
            {"level": "🟡", "message": "品川拠点で3名欠勤予定（明日）"},
            {"level": "🟢", "message": "全体生産性が目標値を達成"}
        ]
        
        for alert in alerts:
            st.write(f"{alert['level']} {alert['message']}")
    
    with col2:
        st.subheader("📋 直近の配置変更")
        changes = [
            "10:30 - 札幌から盛岡へ2名振替",
            "09:45 - 品川でSV補正要員1名追加",
            "09:00 - 沖縄から和歌山へ1名支援"
        ]
        
        for change in changes:
            st.write(change)

def show_allocation_page():
    st.header("👥 全体配置画面")
    
    tab1, tab2 = st.tabs(["現在の配置", "配置変更シミュレーション"])
    
    with tab1:
        st.subheader("現在の人員配置状況")
        
        locations = ["札幌", "盛岡", "品川", "西梅田", "本町東", "沖縄", "佐世保", "和歌山"]
        processes = ["OCR", "エントリ1", "エントリ2", "補正", "SV補正", "目検"]
        
        data = {
            "拠点": locations,
            "OCR": [5, 3, 8, 6, 4, 3, 2, 3],
            "エントリ1": [12, 8, 15, 10, 8, 6, 5, 7],
            "エントリ2": [8, 5, 10, 8, 6, 4, 3, 5],
            "補正": [6, 4, 8, 5, 4, 3, 2, 3],
            "SV補正": [3, 2, 4, 3, 2, 2, 1, 2],
            "目検": [2, 1, 3, 2, 2, 1, 1, 1]
        }
        
        df = pd.DataFrame(data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        st.info("🎨 色が濃いほど配置人数が多いことを示します")
    
    with tab2:
        st.subheader("配置変更シミュレーション")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**変更前の配置**")
            st.dataframe(
                df,
                use_container_width=True,
                height=300,
                hide_index=True
            )
        
        with col2:
            st.write("**変更後の配置（案）**")
            
            df_after = df.copy()
            df_after.loc[df_after["拠点"] == "札幌", "エントリ1"] += 2
            df_after.loc[df_after["拠点"] == "盛岡", "エントリ1"] -= 2
            
            st.dataframe(
                df_after,
                use_container_width=True,
                height=300,
                hide_index=True
            )
        
        st.markdown("---")
        
        st.write("**変更内容**")
        st.success("✅ 盛岡から札幌へエントリ1要員を2名振替")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("生産性への影響", "-5%", "-5%")
        with col2:
            st.metric("納期遵守率", "99.5%", "+1.0%")
        with col3:
            if st.button("この配置を承認", type="primary", use_container_width=True):
                st.success("配置変更を承認しました")

def show_monitoring_page():
    st.header("📊 リアルタイム監視")
    
    tab1, tab2, tab3 = st.tabs(["処理状況", "生産性", "品質"])
    
    with tab1:
        st.subheader("工程別処理状況")
        
        process_data = {
            "工程": ["OCR", "エントリ1", "エントリ2", "補正", "SV補正", "目検"],
            "処理済": [1200, 980, 750, 600, 450, 380],
            "処理中": [150, 200, 180, 120, 80, 50],
            "未処理": [450, 620, 870, 1080, 1270, 1370]
        }
        
        df_process = pd.DataFrame(process_data)
        
        st.bar_chart(
            df_process.set_index("工程")[["処理済", "処理中", "未処理"]],
            use_container_width=True
        )
    
    with tab2:
        st.subheader("拠点別生産性（件/時）")
        
        productivity_data = {
            "拠点": ["札幌", "盛岡", "品川", "西梅田", "本町東", "沖縄", "佐世保", "和歌山"],
            "現在": [450, 380, 520, 480, 420, 350, 300, 340],
            "目標": [500, 450, 550, 500, 450, 400, 350, 400]
        }
        
        df_prod = pd.DataFrame(productivity_data)
        
        st.line_chart(
            df_prod.set_index("拠点"),
            use_container_width=True
        )
    
    with tab3:
        st.subheader("品質指標")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("全体エラー率", "1.2%", "-0.3%")
            st.metric("不読率", "0.8%", "-0.1%")
        
        with col2:
            st.metric("手戻り率", "2.5%", "+0.2%")
            st.metric("品質スコア", "98.5/100", "+1.2")

def show_chat_page():
    st.header("💬 配置調整チャット")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("配置調整の相談を入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = f"""
            承知しました。「{prompt}」について分析します。
            
            現在の状況:
            - 該当拠点の現在配置: エントリ1に12名
            - 現在の生産性: 420件/時
            - 未処理件数: 620件
            
            提案:
            1. 盛岡から2名を一時的に振替（生産性5%低下見込み）
            2. 品川から1名をリモート支援（即時対応可能）
            
            予測される影響:
            - 納期遵守率: 95% → 99.5%
            - 全体生産性: 3,910件/日 → 3,720件/日
            
            この提案を承認しますか？
            """
            st.markdown(response)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("承認", type="primary", use_container_width=True):
                    st.success("配置変更を承認しました")
            with col2:
                if st.button("却下", use_container_width=True):
                    st.info("配置変更を却下しました")
        
        st.session_state.messages.append({"role": "assistant", "content": response})

def show_analytics_page():
    st.header("📈 分析レポート")
    
    st.info("このページは今後実装予定です")
    
    st.subheader("実装予定の機能")
    st.write("""
    - 過去の配置実績分析
    - 生産性トレンド
    - 最適配置の成功事例
    - 工程別ボトルネック分析
    - 拠点別パフォーマンス比較
    """)

def show_settings_page():
    st.header("⚙️ 設定")
    
    st.subheader("データ更新設定")
    
    update_interval = st.slider(
        "自動更新間隔（分）",
        min_value=1,
        max_value=10,
        value=2
    )
    
    st.write(f"データは{update_interval}分ごとに自動更新されます")
    
    st.markdown("---")
    
    st.subheader("アラート設定")
    
    st.checkbox("生産性低下アラート", value=True)
    st.checkbox("納期遅延リスクアラート", value=True)
    st.checkbox("欠勤予定通知", value=True)
    
    st.markdown("---")
    
    st.subheader("表示設定")
    
    st.selectbox(
        "テーマ",
        ["ライト", "ダーク", "自動"]
    )
    
    if st.button("設定を保存", type="primary"):
        st.success("設定を保存しました")

if __name__ == "__main__":
    main()