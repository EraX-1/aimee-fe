#!/usr/bin/env python3
"""
Q1-Q6とQ2（連続）を自動テスト
承認ボタンの動作も確認
"""
import time
from playwright.sync_api import sync_playwright

QUESTIONS = [
    {
        "id": "Q1",
        "text": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
        "expected": "配置変更提案"
    },
    {
        "id": "Q2",
        "text": "配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?",
        "expected": "影響分析",
        "continuous": True  # Q1の続き
    },
    {
        "id": "Q3",
        "text": "SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?",
        "expected": "業務間移動提案"
    },
    {
        "id": "Q4",
        "text": "SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか",
        "expected": "完了時刻予測"
    },
    {
        "id": "Q5",
        "text": "あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか",
        "expected": "工程別配置提案"
    },
    {
        "id": "Q6",
        "text": "現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか",
        "expected": "遅延リスク検出"
    }
]

def send_message(page, textarea, message_text):
    """メッセージを送信"""
    textarea.fill(message_text)
    time.sleep(0.5)
    textarea.press("Enter")
    print(f"✅ 送信完了")

    # 応答待ち
    print("  応答待ち...", end="", flush=True)
    for i in range(60):
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
        print("AIMEE フロントエンドテスト（Q1-Q6 + 承認ボタン）")
        print("=" * 60)

        # アクセス
        page.goto("http://localhost:8501")
        time.sleep(5)

        # テキストエリア取得
        textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first

        # Q1-Q6を順次実行
        for i, q in enumerate(QUESTIONS):
            # Q2はQ1の続きなので、新しいセッションにしない
            if q.get("continuous"):
                print(f"\n--- {q['id']}: {q['expected']} (Q1の続き) ---")
            else:
                print(f"\n--- {q['id']}: {q['expected']} ---")
                if i > 0:
                    # 新しいセッションにするため、ページをリロード
                    page.reload()
                    time.sleep(3)
                    textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first

            # メッセージ送信
            send_message(page, textarea, q['text'])

            # スクリーンショット撮影
            screenshot_path = f"/tmp/streamlit_{q['id']}_response.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"  📸 スクリーンショット: {screenshot_path}")

            # 応答内容を確認
            messages = page.locator('[data-testid="stChatMessage"]')
            if messages.count() > 0:
                last_message = messages.last.inner_text()
                print(f"  応答: {last_message[:150]}...")

                # キーワードチェック
                keywords = {
                    "Q1": ["配置変更", "提案"],
                    "Q2": ["影響", "確認"],
                    "Q3": ["業務間", "移動"],
                    "Q4": ["完了時刻", "予測"],
                    "Q5": ["工程", "人"],
                    "Q6": ["遅延", "リスク"]
                }

                expected_kw = keywords.get(q['id'], [])
                if any(kw in last_message for kw in expected_kw):
                    print(f"  ✅ 期待されるキーワード検出")
                else:
                    print(f"  ⚠️ 期待と異なる応答の可能性")

            # Q1の場合、承認ボタンをクリック
            if q['id'] == "Q1":
                time.sleep(2)
                approve_buttons = page.locator('button:has-text("承認")')
                if approve_buttons.count() > 0:
                    print("\n  【承認ボタンテスト】")
                    approve_buttons.first.click()
                    time.sleep(2)
                    page.screenshot(path="/tmp/streamlit_Q1_approved.png")
                    print("  ✅ 承認ボタンクリック完了")
                    print(f"  📸 承認後: /tmp/streamlit_Q1_approved.png")
                else:
                    print("  ⚠️ 承認ボタンが見つかりません")

        print("\n" + "=" * 60)
        print("✅ 全テスト完了")
        print("=" * 60)
        print("\nスクリーンショット:")
        for q in QUESTIONS:
            print(f"  {q['id']}: /tmp/streamlit_{q['id']}_response.png")
        print(f"  承認: /tmp/streamlit_Q1_approved.png")

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    main()
