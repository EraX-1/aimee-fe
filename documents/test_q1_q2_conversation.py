#!/usr/bin/env python3
"""
Q1→Q2の会話履歴テスト
"""
import requests
import json
import time

API_URL = "http://localhost:8002/api/v1/chat/message"
SESSION_ID = "test_q1_q2_" + time.strftime("%Y%m%d_%H%M%S")

print("=== Q1→Q2 会話履歴テスト ===\n")
print(f"セッションID: {SESSION_ID}\n")

# Q1: 配置転換の提案
print("【Q1】配置転換の提案を依頼")
print("-" * 60)

q1_response = requests.post(
    API_URL,
    json={
        "message": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
        "context": {},
        "session_id": SESSION_ID
    },
    timeout=120
)

if q1_response.status_code == 200:
    q1_data = q1_response.json()
    print("✅ Q1成功")
    print(f"\n応答:\n{q1_data['response'][:300]}...\n")
    print(f"Suggestion: {q1_data.get('suggestion') is not None}")

    if q1_data.get('suggestion'):
        print(f"Suggestion ID: {q1_data['suggestion'].get('id')}")
        print(f"Changes: {len(q1_data['suggestion'].get('changes', []))}件")
        print(f"Changes詳細: {json.dumps(q1_data['suggestion'].get('changes', []), ensure_ascii=False, indent=2)}")
else:
    print(f"❌ Q1失敗: {q1_response.status_code}")
    exit(1)

time.sleep(2)

# Q2: 移動元への影響分析（Q1の提案を参照）
print("\n" + "=" * 60)
print("【Q2】移動元への影響分析を依頼（Q1の提案を参照）")
print("-" * 60)

q2_response = requests.post(
    API_URL,
    json={
        "message": "配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?",
        "context": {},
        "session_id": SESSION_ID
    },
    timeout=120
)

if q2_response.status_code == 200:
    q2_data = q2_response.json()
    print("✅ Q2成功")
    print(f"\n応答:\n{q2_data['response']}\n")

    # 精度チェック
    keywords = ["移動元", "影響"]
    score = sum(1 for kw in keywords if kw in q2_data['response'])

    print(f"\n【精度】: {score}/{len(keywords)} ({score/len(keywords)*100:.0f}%)")

    if "影響分析を行うには" in q2_data['response']:
        print("❌ エラー: 直前の提案が参照されていません")
    else:
        print("✅ 成功: 直前の提案を参照した影響分析が返されました")
else:
    print(f"❌ Q2失敗: {q2_response.status_code}")
