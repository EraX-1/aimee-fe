#!/usr/bin/env python3
"""
AWS環境でQ1をテスト
http://43.207.175.35:8501
"""
import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("=" * 60)
        print("AWS環境テスト")
        print("=" * 60)

        # AWS環境にアクセス
        aws_url = "http://43.207.175.35:8501"
        print(f"\nアクセス: {aws_url}")
        page.goto(aws_url, timeout=60000)
        time.sleep(10)

        # 初期画面スクリーンショット
        page.screenshot(path="/tmp/aws_initial.png", full_page=True)
        print("✅ 初期画面: /tmp/aws_initial.png")

        # Q1を入力
        print("\n--- Q1入力 ---")
        textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first
        textarea.fill("SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。")
        time.sleep(0.5)
        textarea.press("Enter")
        print("送信完了")

        # 応答待ち（最大120秒）
        print("応答待ち...", end="", flush=True)
        for i in range(120):
            time.sleep(1)
            page_content = page.content()
            if "分析中" not in page_content or i > 100:
                print(f" 完了（{i+1}秒）")
                break
            if i % 10 == 9:
                print(".", end="", flush=True)

        # スクロール
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        # 応答スクリーンショット
        page.screenshot(path="/tmp/aws_q1_response.png", full_page=True)
        print("✅ Q1応答: /tmp/aws_q1_response.png")

        # 応答内容確認
        messages = page.locator('[data-testid="stChatMessage"]')
        if messages.count() > 0:
            last_message = messages.last.inner_text()
            print(f"\n応答内容（最初の300文字）:")
            print(last_message[:300])

            # キーワードチェック
            if "配置変更" in last_message or "提案" in last_message:
                print("\n✅ 配置変更提案が表示されました")
            elif "現在のリソースで対応可能" in last_message:
                print("\n⚠️ 「現在のリソースで対応可能です」のみ表示")
            else:
                print("\n⚠️ 不明な応答")

            # 提案expanderを確認
            expanders = page.locator('summary:has-text("提案")')
            if expanders.count() > 0:
                print(f"✅ 提案expander: {expanders.count()}個")
            else:
                print("⚠️ 提案expanderなし")

        print("\n" + "=" * 60)
        print("AWS環境テスト完了")
        print("=" * 60)

        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()
