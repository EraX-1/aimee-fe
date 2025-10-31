#!/usr/bin/env python3
"""
Q1-Q6の最終確認テスト
各質問の応答を確認し、期待通りか判定
"""
import time
from playwright.sync_api import sync_playwright

QUESTIONS = [
    {
        "id": "Q1",
        "text": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
        "expected_keywords": ["配置変更", "提案", "非SS", "SS"],
        "expected_type": "配置変更提案"
    },
    {
        "id": "Q3",
        "text": "SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?",
        "expected_keywords": ["非SS", "SS", "移動"],
        "expected_type": "業務間移動提案"
    },
    {
        "id": "Q4",
        "text": "SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか",
        "expected_keywords": ["完了時刻", "予測", "15:40"],
        "expected_type": "完了時刻予測"
    },
    {
        "id": "Q5",
        "text": "あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか",
        "expected_keywords": ["工程", "配置", "エントリ", "補正"],
        "expected_type": "工程別配置提案"
    },
    {
        "id": "Q6",
        "text": "現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか",
        "expected_keywords": ["遅延", "リスク", "工程"],
        "expected_type": "遅延リスク検出"
    }
]

def send_and_check(page, textarea, question):
    """質問を送信して応答を確認"""
    print(f"\n{'='*60}")
    print(f"{question['id']}: {question['expected_type']}")
    print(f"{'='*60}")

    # メッセージ送信
    textarea.fill(question['text'])
    time.sleep(0.5)
    textarea.press("Enter")
    print("送信完了")

    # 応答待ち
    print("応答待ち...", end="", flush=True)
    for i in range(60):
        time.sleep(1)
        page_content = page.content()
        if "分析中" not in page_content or i > 50:
            print(f" 完了（{i+1}秒）")
            break
        if i % 10 == 9:
            print(".", end="", flush=True)

    # スクロールして応答全体を表示
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)

    # スクリーンショット撮影
    screenshot_path = f"/tmp/final_{question['id']}.png"
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"📸 スクリーンショット: {screenshot_path}")

    # 応答内容を取得
    messages = page.locator('[data-testid="stChatMessage"]')
    if messages.count() > 0:
        last_message = messages.last.inner_text()
        print(f"\n応答内容（最初の200文字）:")
        print(last_message[:200])

        # キーワードチェック
        matched_keywords = [kw for kw in question['expected_keywords'] if kw in last_message]
        print(f"\nキーワードマッチ: {len(matched_keywords)}/{len(question['expected_keywords'])}")
        print(f"  マッチ: {', '.join(matched_keywords)}")

        if len(matched_keywords) >= len(question['expected_keywords']) * 0.5:  # 50%以上
            print(f"✅ {question['id']} パス")
            return True
        else:
            print(f"⚠️ {question['id']} 要確認")
            return False
    else:
        print(f"❌ {question['id']} 失敗（応答なし）")
        return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("="*60)
        print("AIMEE 最終確認テスト (Q1, Q3-Q6)")
        print("="*60)

        # アクセス
        page.goto("http://localhost:8501")
        time.sleep(5)

        results = {}

        # Q1, Q3-Q6を順次テスト（各質問で新しいセッション）
        for i, question in enumerate(QUESTIONS):
            if i > 0:
                # 新しいセッションのためリロード
                page.reload()
                time.sleep(3)

            # テキストエリア取得
            textarea = page.locator('[data-testid="stChatInput"]').locator('textarea').first

            # 質問送信と確認
            passed = send_and_check(page, textarea, question)
            results[question['id']] = passed

        # 結果サマリー
        print("\n" + "="*60)
        print("最終結果")
        print("="*60)

        for qid, passed in results.items():
            status = "✅ パス" if passed else "❌ 失敗"
            print(f"{qid}: {status}")

        passed_count = sum(1 for p in results.values() if p)
        total_count = len(results)
        print(f"\n合格率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")

        print("\nスクリーンショット:")
        for q in QUESTIONS:
            print(f"  {q['id']}: /tmp/final_{q['id']}.png")

        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    main()
