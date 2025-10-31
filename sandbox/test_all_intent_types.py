#!/usr/bin/env python3
"""
全Intent Typeのテストスクリプト
データベースから実データを取得して質問文を生成し、意図解析の精度を確認
"""

import sys
sys.path.append('/Users/umemiya/Desktop/erax/aimee-db')

from config import db_manager
import requests
import json

def get_real_data():
    """データベースから実データを取得"""
    # 拠点名
    locations = db_manager.execute_query("SELECT location_name FROM locations LIMIT 5;")
    location_list = [loc['location_name'] for loc in locations]

    # 工程名
    processes = db_manager.execute_query("SELECT DISTINCT process_name FROM processes WHERE process_name IN ('エントリ1', 'エントリ2', '補正', 'SV補正') LIMIT 5;")
    process_list = [proc['process_name'] for proc in processes]

    # 業務名
    businesses = db_manager.execute_query("SELECT DISTINCT business_category FROM businesses WHERE business_category IN ('SS', '非SS', 'あはき', '適用徴収');")
    business_list = [biz['business_category'] for biz in businesses]

    return {
        'locations': location_list,
        'processes': process_list,
        'businesses': business_list
    }

def generate_test_questions(data):
    """9種類のintent typeに対応する質問文を生成"""
    loc = data['locations'][0] if data['locations'] else '札幌'
    proc = data['processes'][0] if data['processes'] else 'エントリ1'
    biz = data['businesses'][0] if data['businesses'] else 'SS'

    test_cases = [
        {
            "id": "T1",
            "intent_type": "deadline_optimization",
            "question": f"{biz}の新{biz}(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。",
            "expected_entities": {
                "business": biz,
                "deadline_offset_minutes": 20
            }
        },
        {
            "id": "T2",
            "intent_type": "impact_analysis",
            "question": "配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?",
            "expected_entities": {}
        },
        {
            "id": "T3",
            "intent_type": "cross_business_transfer",
            "question": "SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?",
            "expected_entities": {
                "business": "SS"
            }
        },
        {
            "id": "T4",
            "intent_type": "completion_time_prediction",
            "question": "SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか",
            "expected_entities": {}
        },
        {
            "id": "T5",
            "intent_type": "process_optimization",
            "question": "あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか",
            "expected_entities": {
                "business": "あはき"
            }
        },
        {
            "id": "T6",
            "intent_type": "delay_risk_detection",
            "question": "現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか",
            "expected_entities": {}
        },
        {
            "id": "T7",
            "intent_type": "delay_resolution",
            "question": f"{loc}の{proc}が人員不足で遅延しています。対応策を教えてください。",
            "expected_entities": {
                "location": loc,
                "process": proc
            }
        },
        {
            "id": "T8",
            "intent_type": "status_check",
            "question": f"{loc}の現在の配置状況を教えてください",
            "expected_entities": {
                "location": loc
            }
        },
        {
            "id": "T9",
            "intent_type": "general_inquiry",
            "question": "このシステムはどのような機能がありますか？",
            "expected_entities": {}
        }
    ]

    return test_cases

def test_intent_analysis(test_cases):
    """各質問文で意図解析をテストし、結果を確認"""

    print("=" * 80)
    print("全Intent Typeテスト".center(80))
    print("=" * 80)
    print()

    results = []

    for test in test_cases:
        print(f"【{test['id']}】 期待: {test['intent_type']}")
        print(f"質問: {test['question'][:60]}...")

        # APIリクエスト（意図解析のみ）
        response = requests.post(
            "http://localhost:8002/api/v1/chat/message",
            json={
                "message": test['question'],
                "context": {},
                "session_id": f"test_{test['id']}",
                "debug": True  # デバッグモードで詳細取得
            },
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()

            # デバッグ情報から意図解析結果を取得
            debug_info = data.get('debug_info', {})
            intent_analysis = debug_info.get('intent_analysis', {})
            raw_intent = intent_analysis.get('raw_intent', {})

            actual_intent = raw_intent.get('intent_type', 'unknown')
            entities = raw_intent.get('entities', {})

            # 判定
            is_correct = (actual_intent == test['intent_type'])

            result = {
                "id": test['id'],
                "expected": test['intent_type'],
                "actual": actual_intent,
                "correct": is_correct,
                "entities": entities,
                "expected_entities": test['expected_entities']
            }
            results.append(result)

            # 結果表示
            status = "✅" if is_correct else "❌"
            print(f"  結果: {status} {actual_intent}")

            # entities確認
            if test['expected_entities']:
                print(f"  期待entities: {test['expected_entities']}")
                print(f"  実際entities: {entities}")

                # 重要フィールドの確認
                for key, expected_value in test['expected_entities'].items():
                    actual_value = entities.get(key)

                    # 値の比較（数値は文字列として比較）
                    if str(actual_value) == str(expected_value) or actual_value == expected_value:
                        print(f"    ✅ {key}: {actual_value}")
                    else:
                        print(f"    ❌ {key}: 期待={expected_value}, 実際={actual_value}")
        else:
            print(f"  ❌ API失敗: {response.status_code}")
            result = {
                "id": test['id'],
                "expected": test['intent_type'],
                "actual": "error",
                "correct": False
            }
            results.append(result)

        print()

    # サマリー表示
    print("=" * 80)
    print("テスト結果サマリー".center(80))
    print("=" * 80)
    print()

    correct_count = sum(1 for r in results if r['correct'])
    total_count = len(results)
    accuracy = (correct_count / total_count * 100) if total_count > 0 else 0

    print(f"正解数: {correct_count}/{total_count}件")
    print(f"精度: {accuracy:.1f}%")
    print()

    # 不正解の詳細
    incorrect = [r for r in results if not r['correct']]
    if incorrect:
        print("【不正解の詳細】")
        for r in incorrect:
            print(f"  {r['id']}: 期待={r['expected']}, 実際={r['actual']}")
        print()
    else:
        print("🎉 全て正解！")
        print()

    # entitiesの検証
    print("【Entitiesの検証】")
    entity_issues = []
    for r in results:
        if r.get('expected_entities'):
            test_id = r['id']
            expected = r['expected_entities']
            actual = r.get('entities', {})

            for key, exp_val in expected.items():
                act_val = actual.get(key)
                if str(act_val) != str(exp_val) and act_val != exp_val:
                    entity_issues.append(f"{test_id}: {key} 期待={exp_val}, 実際={act_val}")

    if entity_issues:
        for issue in entity_issues:
            print(f"  ❌ {issue}")
    else:
        print("  ✅ 全てのentitiesが正しく抽出されています")

    return results

if __name__ == "__main__":
    print("データベースから実データを取得中...")
    data = get_real_data()

    print(f"取得データ:")
    print(f"  拠点: {data['locations']}")
    print(f"  工程: {data['processes']}")
    print(f"  業務: {data['businesses']}")
    print()

    print("テスト質問文を生成中...")
    test_cases = generate_test_questions(data)
    print(f"生成: {len(test_cases)}件")
    print()

    print("意図解析テスト開始...")
    print()

    results = test_intent_analysis(test_cases)

    # 結果をJSONファイルに保存
    with open('intent_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"結果を intent_test_results.json に保存しました")
