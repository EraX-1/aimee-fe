#!/usr/bin/env python3
"""
Playwrightでフロントエンドを自動テスト
Q1-Q6を実際に入力してスクリーンショットを撮る
"""
import time
from playwright.sync_api import sync_playwright

def test_streamlit_app():
    with sync_playwright() as p:
        # ブラウザ起動（ヘッドレスモード）
        browser = p.chromium.launch(headless=False)  # headless=Falseで画面表示
        page = browser.new_page()

        # Streamlitアプリにアクセス
        print("=" * 60)
        print("フロントエンドにアクセス中...")
        print("=" * 60)
        page.goto("http://localhost:8501")
        time.sleep(5)  # Streamlit初期化待ち

        # 初期画面のスクリーンショット
        page.screenshot(path="/tmp/streamlit_01_initial.png")
        print("✅ 初期画面スクリーンショット: /tmp/streamlit_01_initial.png")

        # Q1を入力
        print("\n" + "=" * 60)
        print("Q1を入力中...")
        print("=" * 60)

        # Streamlitのテキスト入力欄を探す
        # st.text_input または st.chat_input を使っている可能性がある

        # chat_inputを探す
        try:
            # Streamlitのchat_input内のtextarea要素を探す
            # まずchat_inputコンテナを見つける
            chat_container = page.locator('[data-testid="stChatInput"]')

            if chat_container.count() > 0:
                print("✅ チャット入力コンテナを発見")

                # その中のtextarea要素を探す
                textarea = chat_container.locator('textarea').first

                if textarea.count() > 0:
                    print("✅ テキストエリアを発見")
                    textarea.fill("SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。")
                    page.screenshot(path="/tmp/streamlit_02_q1_input.png")
                    print("✅ Q1入力後スクリーンショット: /tmp/streamlit_02_q1_input.png")

                    # Enterで送信
                    textarea.press("Enter")
                    print("✅ Q1送信完了")
                else:
                    # 代替: 全てのtextareaから探す
                    all_textareas = page.locator('textarea')
                    print(f"全textarea数: {all_textareas.count()}")
                    if all_textareas.count() > 0:
                        textarea = all_textareas.last  # 最後のtextarea（chat_inputの可能性が高い）
                        textarea.fill("SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。")
                        page.screenshot(path="/tmp/streamlit_02_q1_input.png")
                        print("✅ Q1入力（代替方法）")
                        textarea.press("Enter")
                        print("✅ Q1送信完了")

                # 応答待ち（最大60秒）
                print("応答待ち中...")

                # 「分析中...」が消えるまで待つ
                max_wait = 60
                for i in range(max_wait):
                    time.sleep(1)
                    page_text = page.content()
                    if i % 5 == 0:
                        print(f"  待機中... {i}秒")

                    # 「分析中」がなくなったら完了
                    if "分析中" not in page_text:
                        print(f"✅ 応答完了（{i}秒）")
                        break
                else:
                    print("⚠️ タイムアウト（60秒）")

                # 応答後のスクリーンショット
                page.screenshot(path="/tmp/streamlit_03_q1_response.png")
                print("✅ Q1応答後スクリーンショット: /tmp/streamlit_03_q1_response.png")

                # ページ内容を確認
                page_content = page.content()

                # 提案カードがあるか確認
                if "配置変更" in page_content or "提案" in page_content:
                    print("✅ 提案カードが表示されています")
                elif "現在のリソースで対応可能" in page_content:
                    print("⚠️ 「現在のリソースで対応可能です」のみ表示")
                else:
                    print("⚠️ 不明な応答")

                # チャットメッセージを取得
                messages = page.locator('[data-testid="stChatMessage"]')
                if messages.count() > 0:
                    print(f"\nチャットメッセージ数: {messages.count()}件")
                    for i in range(min(3, messages.count())):
                        msg_text = messages.nth(i).inner_text()
                        print(f"  メッセージ{i+1}: {msg_text[:100]}...")
                else:
                    print("⚠️ チャットメッセージが見つかりません")

            else:
                print("❌ チャット入力欄が見つかりません")
                # 代替: text_inputを探す
                text_inputs = page.locator('input[type="text"]')
                print(f"テキスト入力欄の数: {text_inputs.count()}")

        except Exception as e:
            print(f"❌ エラー: {e}")
            page.screenshot(path="/tmp/streamlit_error.png")

        # 最終スクリーンショット
        page.screenshot(path="/tmp/streamlit_04_final.png", full_page=True)
        print("\n✅ 最終スクリーンショット: /tmp/streamlit_04_final.png")

        # ブラウザを5秒間保持（確認用）
        print("\nブラウザを5秒間保持します...")
        time.sleep(5)

        browser.close()
        print("\n✅ テスト完了")

if __name__ == "__main__":
    test_streamlit_app()
