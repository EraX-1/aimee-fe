# Q1 完全ガイド - 納期最適化

**最終更新**: 2025-10-27
**Intent Type**: deadline_optimization

---

## 📝 Q1の質問文

```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```

---

## 🎯 Q1の目的

**納期に間に合わせるための最適な人員配置を提案する**

- 納期の20分前に処理完了させたい
- 現在のリソースで対応可能かを判定
- 不足がある場合は配置変更を提案
- 不足がない場合は詳細な理由を説明

---

## 🔄 処理フロー（5ステップ）

### STEP 1: 意図解析（gemma2:2b）⏱️ 約2秒

**入力**: 質問文

**処理内容**:
- LLM（gemma2:2b）で意図を分析
- Intent Typeを分類
- 4階層情報とその他情報を抽出

**出力**:
```json
{
  "intent_type": "deadline_optimization",
  "urgency": "high",
  "requires_action": true,
  "entities": {
    "location": null,
    "business_category": "SS",
    "business_name": "新SS(W)",
    "process_category": null,
    "process_name": null,
    "deadline_offset_minutes": 20,
    "target_people_count": null
  }
}
```

**抽出ルール**:
- ✅ メッセージに明記されている情報のみ抽出
- ❌ 推測で値を入れない
- ❌ 助詞（「の」「が」）を含めない
- ✅ 値のみを設定

**4階層構造**:
1. **business_category**（業務大分類）: SS、非SS、あはき、適用徴収
2. **business_name**（業務名）: 新SS(W)、非SS(W)、はり・きゅう など
3. **process_category**（OCR区分）: OCR対象、OCR非対象、目検
4. **process_name**（工程名）: エントリ1、エントリ2、補正、SV補正、目検

---

### STEP 2: RAG検索（ChromaDB）⏱️ 約0.3秒

**処理内容**:
- ChromaDBから管理者ノウハウを検索
- 類似度スコアで関連するルールを取得

**データソース**:
- aimee_knowledge コレクション（12件）
- 管理者の判断基準

**出力例**:
```
検索結果: 0件（現在は該当するルールなし）
```

---

### STEP 3: データベース照会（MySQL）⏱️ 約1秒

**処理内容**:
1. progress_snapshotsから進捗データ取得
2. オペレータとスキル情報取得
3. 余剰・不足の判定

**実行されるクエリ**:

#### 3-1. 進捗データ取得
```sql
SELECT
    snapshot_time,           -- 現在時刻
    expected_completion_time, -- 納期
    total_waiting,            -- 残タスク数
    processing,
    entry_count
FROM progress_snapshots
WHERE total_waiting > 0       -- 処理中のデータのみ
ORDER BY snapshot_time DESC   -- 受信時刻が新しい順
LIMIT 10;
```

**取得データ例**:
```
受信時刻: 202507281240（12:40）
納期: 202507281540（15:40）
残タスク: 947件
```

#### 3-2. オペレータ・スキル情報取得
```sql
SELECT
    l.location_name,
    b.business_category,
    b.business_name,
    p.process_category,
    p.process_name,
    COUNT(DISTINCT o.operator_id) as operator_count
FROM operators o
JOIN operator_process_capabilities opc ON o.operator_id = opc.operator_id
JOIN locations l ON o.location_id = l.location_id
JOIN businesses b ON opc.business_id = b.business_id
JOIN processes p ON opc.business_id = p.business_id AND opc.process_id = p.process_id
WHERE o.is_valid = 1
GROUP BY l.location_name, b.business_category, b.business_name,
         p.process_category, p.process_name
ORDER BY b.business_category, p.process_name, l.location_name;
```

**取得データ例**:
```
余剰候補: 60件（3名以上いる拠点・工程）
不足候補: 0件（1名しかいない拠点・工程）
```

#### 3-3. スキルベースマッチング用データ取得
```sql
SELECT
    o.operator_name,
    p_target.process_name as target_process_name,   -- 移動先スキル
    p_current.process_name as current_process_name, -- 現在の配置
    b_target.business_category,
    b_target.business_name
FROM operators o
JOIN operator_process_capabilities opc_target ON o.operator_id = opc_target.operator_id
LEFT JOIN operator_process_capabilities opc_current ON o.operator_id = opc_current.operator_id
WHERE o.is_valid = 1
  AND p_target.process_name IN ('エントリ1', 'エントリ2', '補正', 'SV補正', '目検')
  AND opc_target.work_level >= 1;
```

**取得データ例**:
```
22,000件のスキル保有データ
エントリ1のスキル保有者: 17,600人
→ 現在エントリ2に配置中の人を特定可能
```

---

### STEP 4: 提案生成（スキルベースマッチング）⏱️ 約0.2秒

**処理内容**:

#### ケース1: 不足がある場合
1. 不足工程のスキルを持つオペレータを全検索
2. 現在の配置工程を確認
3. 異なる工程に配置中なら移動候補とする
4. 業務間移動を優先
5. 配置変更案を生成（4階層構造）

**出力例**:
```json
{
  "changes": [
    {
      "from_business_category": "非SS",
      "from_business_name": "非SS(W)",
      "from_process_category": "OCR対象",
      "from_process_name": "エントリ2",
      "to_business_category": "SS",
      "to_business_name": "新SS(W)",
      "to_process_category": "OCR対象",
      "to_process_name": "エントリ1",
      "count": 2,
      "operators": ["竹下　朱美", "高山　麻由子"],
      "is_cross_business": true
    }
  ]
}
```

#### ケース2: 不足がない場合（Q1の現状）

**判定ロジック**:
```python
if len(shortage_list) == 0:
    # 配置提案は生成しない
    changes = []
```

**詳細理由を自動生成**:
```python
def _generate_no_shortage_reason(db_data):
    # progress_snapshotsから取得
    current_time = "12:40"
    deadline = "15:40"
    remaining_minutes = 180
    total_waiting = 947

    # 処理速度計算
    required_speed = 947 / 180 = 5.3件/分
    estimated_speed = 7.5件/分（推定）

    # 判定
    if required_speed <= estimated_speed:
        return "問題なし"
```

---

### STEP 5: 応答生成（gemma3:4b）⏱️ 約3秒

**入力**:
- 意図解析結果
- データベース情報
- 配置提案（changesが空の場合もある）

**処理内容**:

#### ケース1: 不足がある場合
LLM（gemma3:4b）で自然言語応答を生成

#### ケース2: 不足がない場合（Q1の現状）
**LLMを使わず、Pythonで直接生成**:
```python
response_text = f"""✅ 現在のリソースで対応可能です

【分析結果】
- 現在時刻: {current_time}
- 納期: {deadline_time}（あと{remaining_minutes}分）
- 残タスク数: {total_waiting}件
- 必要処理速度: {required_speed:.1f}件/分
- 現在の処理能力: 約{estimated_current_speed}件/分（推定）
- 判定: ✅ 問題なし

【結論】
このまま進めれば{remaining_minutes}分以内に完了できます

追加の人員配置は不要と判断します。"""
```

**出力（実際の応答）**:
```
✅ 現在のリソースで対応可能です

【分析結果】
- 現在時刻: 12:40
- 納期: 15:40（あと180分）
- 残タスク数: 947件
- 必要処理速度: 5.3件/分
- 現在の処理能力: 約7.5件/分（推定）
- 判定: ✅ 問題なし

【結論】
このまま進めれば180分以内に完了できます

追加の人員配置は不要と判断します。
```

---

## 📊 処理時間

| ステップ | 処理内容 | 時間 |
|---------|---------|------|
| STEP 1 | 意図解析（gemma2:2b） | 2秒 |
| STEP 2 | RAG検索（ChromaDB） | 0.3秒 |
| STEP 3 | DB照会（MySQL） | 1秒 |
| STEP 4 | 提案生成（Python） | 0.2秒 |
| STEP 5 | 応答生成（Python直接） | 0.1秒 |
| **合計** | | **約3.6秒** |

**注**: 不足がある場合はSTEP 5でLLM（gemma3:4b）を使用するため+3秒

---

## 🎯 現在の動作（2025-10-27最新版）

### 入力
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```

### 出力
```
✅ 現在のリソースで対応可能です

【分析結果】
- 現在時刻: 12:40
- 納期: 15:40（あと180分）
- 残タスク数: 947件
- 必要処理速度: 5.3件/分
- 現在の処理能力: 約7.5件/分（推定）
- 判定: ✅ 問題なし

【結論】
このまま進めれば180分以内に完了できます

追加の人員配置は不要と判断します。
```

**配置変更提案**: なし（不足がないため）

---

## 💡 使い方

### 基本的な使い方

**ローカル環境**:
```
http://localhost:8501
```

チャット画面で質問を入力:
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```

---

### デバッグモード

**URL**:
```
http://localhost:8501/?debug=1
```

**表示される情報**:
- 意図解析結果（Intent Type、4階層情報）
- 実行されたSQL文とレコード数
- RAG検索結果と類似度スコア
- スキルマッチング詳細
- 処理時間内訳

---

### APIで直接テスト

```bash
curl -X POST http://localhost:8002/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。",
    "debug": true
  }'
```

---

## 📚 必要なデータ

### 1. operators（オペレータマスタ）
**必要件数**: 100件

**サンプル**:
```
operator_id: a0301930
operator_name: 竹下　朱美
location_id: 91（札幌）
is_valid: 1
```

---

### 2. operator_process_capabilities（スキル情報）
**必要件数**: 55,863件

**サンプル**:
```
operator_id: a0301930
business_id: 523201（新SS(W)）
process_id: 152（エントリ1）
work_level: 1
```

**重要な構成**:
- SS業務のスキル保有者: 100人
- 非SS業務のスキル保有者: 100人
- 1人あたり平均22工程のスキル保有

---

### 3. progress_snapshots（進捗スナップショット）
**必要件数**: 832件

**サンプル**:
```
snapshot_time: 202507281240（12:40）
expected_completion_time: 202507281540（15:40）
total_waiting: 947件
processing: 49件
```

**重要なポイント**:
- WHERE total_waiting > 0（処理中のデータのみ）
- ORDER BY snapshot_time DESC（受信時刻順）
- → 2025年7月28日12:40のデータを取得

---

### 4. businesses（業務マスタ）
**必要件数**: 12件

**4種類の業務大分類**:
- SS（4業務）
- 非SS（4業務）
- あはき（2業務）
- 適用徴収（2業務）

---

### 5. processes（工程マスタ）
**必要件数**: 46件

**主要な工程**:
- エントリ1、エントリ2
- 補正、SV補正
- 目検

---

## 🔧 データ復元方法

### データが壊れた・消えた場合

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_all_data.sh
```

**実行内容**:
- 自動バックアップ作成
- 全データクリア
- operator_process_capabilities投入（55,863件）
- progress_snapshots投入（832件）
- ChromaDB投入（12件）

**所要時間**: 約3分

---

## ⚙️ 設定

### 使用モデル

**意図解析**: gemma2:2b（20億パラメータ）
```
OLLAMA_LIGHT_PORT=11435
INTENT_MODEL=gemma2:2b
```

**応答生成**: gemma3:4b（40億パラメータ）
```
OLLAMA_MAIN_PORT=11435
MAIN_MODEL=gemma3:4b
```

---

### データベース設定

**ローカル環境**:
```
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@localhost:3306/aimee_db
```

**AWS環境（RDS）**:
```
DATABASE_URL=mysql+aiomysql://admin:Aimee2024!RDS@aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306/aimee_db
```

---

## 🎨 応答パターン

### パターン1: 不足なし（現在の状態）

**条件**: 余剰候補はあるが、不足候補がない

**応答**:
```
✅ 現在のリソースで対応可能です

【分析結果】
- 現在時刻: 12:40
- 納期: 15:40（あと180分）
- 残タスク数: 947件
- 必要処理速度: 5.3件/分
- 現在の処理能力: 約7.5件/分（推定）
- 判定: ✅ 問題なし

【結論】
このまま進めれば180分以内に完了できます
```

**配置変更提案**: なし

---

### パターン2: 不足あり（データを調整した場合）

**条件**: 特定の拠点・工程で人員が不足（1名のみ）

**応答例**:
```
札幌のエントリ1工程で人員が不足しています。
以下の配置変更を提案します:

- 「非SS」の「非SS(W)」の「OCR対象」の「エントリ2」から
  竹下　朱美さんを「SS」の「新SS(W)」の「OCR対象」の「エントリ1」へ移動

- 「非SS」の「非SS(W)」の「OCR対象」の「エントリ2」から
  高山　麻由子さんを「SS」の「新SS(W)」の「OCR対象」の「エントリ1」へ移動
```

**配置変更提案**: あり（2件など）

---

## 🔍 トラブルシューティング

### Q1で「現在のリソースで対応可能」としか表示されない

**原因**: progress_snapshotsが空または古いデータ

**確認方法**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as c FROM progress_snapshots WHERE total_waiting > 0;')
print(f'progress_snapshots（処理中）: {result[0][\"c\"]}件')
"
```

**期待値**: 584件以上

**解決方法**:
```bash
./restore_all_data.sh
```

---

### Q1で「処理完了時刻の予測」が表示される

**原因**: Intent Typeが誤判定（completion_time_prediction）

**確認方法**:
デバッグモード（?debug=1）で意図解析結果を確認

**解決方法**:
- 既に修正済み
- 「配置したい」「最適配置」があればdeadline_optimizationと判定

---

### Q1で提案が30件も表示される

**原因**: 不足がないのに効率化提案を生成していた（修正済み）

**現在の動作**:
- 不足がない場合は提案を出さない
- 詳細な理由を表示する

---

## 📝 関連ドキュメント

- **[README.md](README.md)**: Q1～Q6の質問文一覧
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)**: システム全体図
- **[CHANGELOG.md](CHANGELOG.md)**: 実装履歴
- **[test_all_intent_types.py](test_all_intent_types.py)**: Intent Typeテスト
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)**: 全情報

---

## 🎯 今後の拡張

### 次回実装予定

1. **deadline_offset_minutes を計算に使用**
   - 現在: 抽出はできているが計算に未使用
   - 実装: 「20分前」→目標15:20として計算
   - 所要時間: 約10分

2. **リアルタイムデータ連携**
   - 現在: 2025年7月の静的データ
   - 実装: RealWorksManager APIから最新データ取得
   - バッチで定期的に更新

3. **承認/否認履歴の学習**
   - 現在: approval_historyに蓄積のみ
   - 実装: 承認されたパターンを学習してAI精度向上

---

**作成日**: 2025-10-27
**バージョン**: 2.0.0
