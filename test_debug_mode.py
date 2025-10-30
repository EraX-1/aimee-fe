#!/usr/bin/env python3
"""
デバッグモード（?debug=1）でQ1-Q6をテスト
デバッグ情報が正しく表示されるか確認
"""
import time
from playwright.sync_api import sync_playwright

QUESTIONS = [
    {
        "id": "Q1",
        "text": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
        "expected_debug": ["意図解析", "SQL", "RAG", "intent_type"]
    },
    {
        "id": "Q4",
        "text": "SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか",
        "expected_debug": ["意図解析", "completion_time_prediction"]
    },
    {
        "id": "Q5",
        "text": "あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか",
        "expected_debug": ["意図解析", "process_optimization", "あはき"]
    }
]

def send_message(page, textarea, message_text):
    """メッセージを送信"""
    textarea.fill(message_text)
    time.sleep(0.5)
    textarea.press("Enter")
    print(f"  送信完了")

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
        print("デバッグモードテスト（?debug=1）")
        print("=" * 60)

        # デバッグモード付きでアクセス
        print("\nアクセス: http://localhost:8501/?debug=1")
        page.goto("http://localhost:8501/?debug=1")
        time.sleep(5)

        # 初期画面スクリーンショット
        page.screenshot(path="/tmp/debug_initial.png", full_page=True)
        print("✅ 初期画面: /tmp/debug_initial.png")

        # デバッグモード表示確認
        page_content = page.content()
        if "デバッグ" in page_content or "debug" in page_content.lower():
            print("✅ デバッグモードが有効化されています")
        else:
            print("⚠️ デバッグモードの表示が見つかりません")

        # Q1, Q4, Q5をテスト
        for i, question in enumerate(QUESTIONS):
            if i > 0:
                # 新しいセッション
                page.goto("http://localhost:8501/?debug=1")
                time.sleep(3)

            print(f"\n{'='*60}")
            print(f"{question['id']}: デバッグ情報確認")
            print(f"{'='*60}")

            # テキストエリア取得
            textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first

            # メッセージ送信
            send_message(page, textarea, question['text'])

            # スクロールして全体を表示
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

            # スクリーンショット
            screenshot_path = f"/tmp/debug_{question['id']}.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"  📸 スクリーンショット: {screenshot_path}")

            # デバッグ情報を確認
            page_text = page.content()

            # 期待されるデバッグ情報があるか確認
            matched = []
            missing = []
            for debug_kw in question['expected_debug']:
                if debug_kw in page_text:
                    matched.append(debug_kw)
                else:
                    missing.append(debug_kw)

            print(f"\n  デバッグ情報:")
            print(f"    ✅ 検出: {', '.join(matched)}")
            if missing:
                print(f"    ⚠️ 未検出: {', '.join(missing)}")

            # デバッグexpanderを探す
            debug_expanders = page.locator('summary:has-text("デバッグ")')
            if debug_expanders.count() > 0:
                print(f"  ✅ デバッグexpander発見: {debug_expanders.count()}個")

                # 最初のデバッグexpanderをクリック
                debug_expanders.first.click()
                time.sleep(1)

                # 展開後のスクリーンショット
                expanded_screenshot = f"/tmp/debug_{question['id']}_expanded.png"
                page.screenshot(path=expanded_screenshot, full_page=True)
                print(f"  📸 展開後: {expanded_screenshot}")
            else:
                print(f"  ⚠️ デバッグexpanderが見つかりません")

            # 判定
            if len(matched) >= len(question['expected_debug']) * 0.5:
                print(f"  ✅ {question['id']} デバッグ情報パス")
            else:
                print(f"  ❌ {question['id']} デバッグ情報不足")

        print("\n" + "=" * 60)
        print("デバッグモードテスト完了")
        print("=" * 60)
        print("\nスクリーンショット:")
        for q in QUESTIONS:
            print(f"  {q['id']}: /tmp/debug_{q['id']}.png")
            print(f"  {q['id']} (展開): /tmp/debug_{q['id']}_expanded.png")

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    main()
