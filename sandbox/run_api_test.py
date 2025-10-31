#!/usr/bin/env python3
"""
Q1~Q6のAPIテストを実施して精度を検証
"""
import requests
import json
import time

API_URL = "http://localhost:8002/api/v1/chat/message"

# テストケースを読み込み
with open('documents/test_cases_q1_q6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    test_cases = data['test_cases']

results = []
session_id = "test_session_" + time.strftime("%Y%m%d_%H%M%S")

print("=== AIMEE APIテスト開始 ===\n")
print(f"セッションID: {session_id}\n")

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"【{test['id']}】{test['question'][:50]}...")
    print(f"{'='*60}")

    # API呼び出し
    try:
        response = requests.post(
            API_URL,
            json={
                "message": test['question'],
                "context": {},
                "session_id": session_id
            },
            timeout=120
        )

        if response.status_code == 200:
            result_data = response.json()
            response_text = result_data.get('response', '')
            manager_rules = result_data.get('rag_results', {}).get('manager_rules', [])
            suggestion = result_data.get('suggestion')

            print(f"\n【応答】")
            print(response_text[:500])

            if manager_rules:
                print(f"\n【管理者ルール取得】: {len(manager_rules)}件")
                for rule in manager_rules:
                    print(f"  - {rule.get('title', '')[:40]}")

            if suggestion:
                print(f"\n【提案あり】: {len(suggestion.get('changes', []))}件の配置変更")

            # 精度チェック
            score = 0
            total_checks = len(test['should_include'])

            for keyword in test['should_include']:
                if keyword in response_text:
                    score += 1
                else:
                    print(f"  ⚠️ 欠落: '{keyword}'")

            accuracy = (score / total_checks * 100) if total_checks > 0 else 0
            print(f"\n【精度】: {accuracy:.0f}% ({score}/{total_checks})")

            results.append({
                "id": test['id'],
                "accuracy": accuracy,
                "response": response_text,
                "has_manager_rules": len(manager_rules) > 0,
                "has_suggestion": suggestion is not None
            })
        else:
            print(f"❌ エラー: {response.status_code}")
            results.append({"id": test['id'], "accuracy": 0, "error": response.status_code})

    except Exception as e:
        print(f"❌ 例外: {e}")
        results.append({"id": test['id'], "accuracy": 0, "error": str(e)})

    time.sleep(2)  # 連続リクエスト回避

# 総合精度を計算
print(f"\n\n{'='*60}")
print("【総合結果】")
print(f"{'='*60}")

total_accuracy = sum([r.get('accuracy', 0) for r in results]) / len(results)
print(f"\n総合精度: {total_accuracy:.1f}%")

for r in results:
    status = "✅" if r.get('accuracy', 0) >= 70 else "⚠️" if r.get('accuracy', 0) >= 50 else "❌"
    print(f"{status} {r['id']}: {r.get('accuracy', 0):.0f}%")

# 結果を保存
with open('api_test_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_accuracy": total_accuracy,
        "results": results
    }, f, ensure_ascii=False, indent=2)

print(f"\n結果を api_test_results.json に保存しました")

if total_accuracy >= 90:
    print(f"\n🎉 目標達成! 精度90%以上")
else:
    print(f"\n⚠️ 精度改善が必要: 目標90% - 現在{total_accuracy:.1f}%")
