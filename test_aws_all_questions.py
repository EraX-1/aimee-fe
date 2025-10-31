#!/usr/bin/env python3
"""
AWS環境でQ1-Q6全質問をテスト
http://43.207.175.35:8501
"""
import time
from playwright.sync_api import sync_playwright

QUESTIONS = [
    {
        "id": "Q1",
        "text": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
        "expected": ["配置変更", "提案", "非SS"]
    },
    {
        "id": "Q3",
        "text": "SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?",
        "expected": ["非SS", "SS", "移動"]
    },
    {
        "id": "Q4",
        "text": "SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか",
        "expected": ["完了時刻", "予測", "15:40"]
    },
    {
        "id": "Q5",
        "text": "あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか",
        "expected": ["工程", "配置", "エントリ"]
    },
    {
        "id": "Q6",
        "text": "現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか",
        "expected": ["遅延", "リスク"]
    }
]

def send_message(page, textarea, message_text):
    """メッセージを送信して応答を待つ"""
    textarea.fill(message_text)
    time.sleep(0.5)
    textarea.press("Enter")

    # 応答待ち（最大120秒）
    for i in range(120):
        time.sleep(1)
        page_content = page.content()
        if "分析中" not in page_content or i > 100:
            return i + 1
        if i % 10 == 9:
            print(".", end="", flush=True)
    return 120

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("=" * 60)
        print("AWS環境 Q1-Q6全質問テスト")
        print("=" * 60)

        aws_url = "http://43.207.175.35:8501"
        results = {}

        for i, q in enumerate(QUESTIONS):
            print(f"\n{'='*60}")
            print(f"{q['id']}: {q['text'][:50]}...")
            print(f"{'='*60}")

            # 新しいセッションのためリロード（Q1以外）
            if i > 0:
                page.goto(aws_url, timeout=60000)
                time.sleep(5)
            else:
                page.goto(aws_url, timeout=60000)
                time.sleep(10)

            # テキストエリア取得
            textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first

            # メッセージ送信
            print("送信中...", end="", flush=True)
            response_time = send_message(page, textarea, q['text'])
            print(f" 応答完了（{response_time}秒）")

            # スクロールして応答全体を表示
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

            # スクリーンショット
            screenshot_path = f"/tmp/aws_{q['id']}_response.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 スクリーンショット: {screenshot_path}")

            # 応答内容を確認
            messages = page.locator('[data-testid="stChatMessage"]')
            if messages.count() > 0:
                last_message = messages.last.inner_text()
                print(f"\n応答内容（最初の200文字）:")
                print(last_message[:200])

                # キーワードチェック
                matched = [kw for kw in q['expected'] if kw in last_message]
                print(f"\nキーワードマッチ: {len(matched)}/{len(q['expected'])}")
                print(f"  マッチ: {', '.join(matched) if matched else 'なし'}")

                if len(matched) >= len(q['expected']) * 0.5:
                    print(f"✅ {q['id']} パス")
                    results[q['id']] = True
                else:
                    print(f"⚠️ {q['id']} 要確認")
                    results[q['id']] = False
            else:
                print(f"❌ {q['id']} 応答なし")
                results[q['id']] = False

        # 結果サマリー
        print("\n" + "=" * 60)
        print("AWS環境テスト結果")
        print("=" * 60)

        for qid, passed in results.items():
            status = "✅ パス" if passed else "❌ 失敗"
            print(f"{qid}: {status}")

        passed_count = sum(1 for p in results.values() if p)
        total_count = len(results)
        print(f"\n合格率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")

        print("\nスクリーンショット:")
        for q in QUESTIONS:
            print(f"  {q['id']}: /tmp/aws_{q['id']}_response.png")

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    main()
