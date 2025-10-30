#!/usr/bin/env python3
"""
Q1→Q2を連続して入力（ページリロードなし）
会話履歴機能の動作確認
"""
import time
from playwright.sync_api import sync_playwright

def send_message(page, textarea, message_text, wait_seconds=60):
    """メッセージを送信して応答を待つ"""
    textarea.fill(message_text)
    time.sleep(0.5)
    textarea.press("Enter")
    print(f"  送信完了")

    # 応答待ち
    print(f"  応答待ち...", end="", flush=True)
    for i in range(wait_seconds):
        time.sleep(1)
        page_content = page.content()
        if "分析中" not in page_content or i > 50:
            print(f" 完了（{i+1}秒）")
            return True
        if i % 10 == 9:
            print(".", end="", flush=True)

    print(" タイムアウト")
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("=" * 60)
        print("Q1→Q2 連続テスト（会話履歴確認）")
        print("=" * 60)

        # アクセス
        page.goto("http://localhost:8501")
        time.sleep(5)

        # テキストエリア取得
        textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first

        # Q1を送信
        print("\n--- Q1: 配置変更提案 ---")
        send_message(page, textarea, "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。")

        # Q1のスクリーンショット
        page.screenshot(path="/tmp/streamlit_Q1_continuous.png", full_page=True)
        print("  📸 スクリーンショット: /tmp/streamlit_Q1_continuous.png")

        # Q1の応答を確認
        messages = page.locator('[data-testid="stChatMessage"]')
        if messages.count() > 0:
            last_message = messages.last.inner_text()
            print(f"  応答: {last_message[:150]}...")

            if "配置変更" in last_message or "提案" in last_message:
                print("  ✅ Q1: 配置変更提案が表示されました")
            else:
                print("  ⚠️ Q1: 期待と異なる応答")

        # 少し待機
        time.sleep(2)

        # Q2を送信（同じページ、リロードなし）
        print("\n--- Q2: 影響分析（Q1の直後、同じセッション） ---")
        send_message(page, textarea, "配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?")

        # Q2のスクリーンショット
        page.screenshot(path="/tmp/streamlit_Q2_continuous.png", full_page=True)
        print("  📸 スクリーンショット: /tmp/streamlit_Q2_continuous.png")

        # Q2の応答を確認
        messages = page.locator('[data-testid="stChatMessage"]')
        if messages.count() > 0:
            last_message = messages.last.inner_text()
            print(f"  応答: {last_message[:200]}...")

            if "影響" in last_message and ("移動元" in last_message or "確認" in last_message):
                print("  ✅ Q2: 影響分析が表示されました")
            elif "配置変更" in last_message or "提案" in last_message:
                print("  ❌ Q2: 配置変更提案が表示されました（影響分析ではない）")
            else:
                print("  ⚠️ Q2: 不明な応答")

        # 最終スクリーンショット
        page.screenshot(path="/tmp/streamlit_Q1_Q2_final.png", full_page=True)
        print("\n✅ 最終スクリーンショット: /tmp/streamlit_Q1_Q2_final.png")

        print("\n" + "=" * 60)
        print("テスト完了")
        print("=" * 60)

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    main()
