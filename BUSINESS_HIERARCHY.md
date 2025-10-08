# 業務分類の階層構造 (RW Manager)

## 📊 画像から読み取った業務階層

### 🔍 4つの大分類

RW Managerでは、業務は以下の**4つの大分類**に分かれています:

1. **SS (社会保険)** - `SS.png`
2. **非SS** - `非SS.png`
3. **あはき (はり・きゅう・あんまマッサージ)** - `あはき.png`
4. **適用徴収** - `適用徴収.png`

---

## 📋 各大分類の詳細階層

### 1️⃣ SS (社会保険)

#### 第1階層: 業務タイプ
- **新SS(W)** - 業務ID: `523201`
- **新SS(片道)** - 業務ID: `523202`
- **新SS+(W)** - 業務ID: `523401`
- **新SS+(片道)** - 業務ID: `523402`

#### 第2階層: OCR区分
各業務タイプの中で、さらに以下に分類:
- **OCR対象**
- **OCR非対象**

#### 第3階層: 工程名
各OCR区分の中で、さらに工程に分類:
- **エントリ1** (process_id: `152` or `252`)
- **エントリ2** (process_id: `112`, `212`, `452`)
- **補正** (process_id: `104`, `204`)
- **SV補正** (process_id: `116`, `216`)
- **目検** (process_id: `027`)

**階層構造の例**:
```
SS
└─ 新SS(W) [523201]
   ├─ OCR対象
   │  ├─ エントリ1 [152]
   │  ├─ エントリ2 [452]
   │  ├─ 補正 [104]
   │  └─ SV補正 [116]
   └─ OCR非対象
      ├─ エントリ1 [252]
      ├─ エントリ2 [212]
      ├─ 補正 [204]
      └─ SV補正 [216]
```

---

### 2️⃣ 非SS

#### 第1階層: 業務タイプ
- **非SS(W)** - 業務ID: `523301`
- **非SS(片道)** - 業務ID: `523302`
- **非SS(保険者間調整)(W)** - 業務ID: `523501`
- **非SS(保険者間調整)(片道)** - 業務ID: `523502`
- **非SS(柔整専用回線業務)(W)** - 業務ID: `523603`
- **非SS(柔整専用回線業務)(片道)** - 業務ID: `523604`

#### 第2階層: OCR区分
- **OCR対象**
- **OCR非対象**
- **目検** (一部業務のみ)

#### 第3階層: 工程名
- **エントリ1**
- **エントリ2**
- **補正**
- **SV補正**

---

### 3️⃣ あはき (はり・きゅう・あんまマッサージ)

#### 第1階層: 業務タイプ
- **はり・きゅう** - 業務ID: `1434951:10:00`
- **あんまマッサージ** - 業務ID: `1435117:50:00`

#### 第2階層: 処理区分
- **日報対象処理**
- **日報外処理**

#### 第3階層: 工程名
- **エントリ1**
- **エントリ2**
- **補正**
- **SV補正**

---

### 4️⃣ 適用徴収

#### 第1階層: 業務タイプ
- **新SS+(W)** - 業務ID: `523401`
- **新SS+(片道)** - 業務ID: `523402`

#### 第2階層: OCR区分
- **OCR対象**
- **OCR非対象**

#### 第3階層: 工程名
- **エントリ1**
- **エントリ2**
- **補正**
- **SV補正**

---

## 🎯 AIが出力すべき回答形式

### 要求された回答例

ユーザーからの要望:
```
「SS」の「新SS(W)」の「OCR対象」の「エントリ1」に◯◯さん、◯◯さんを移動してください。
```

### 完全な階層パス表示

AIの回答には、以下の**4階層**を含める必要があります:

1. **大分類** (SS / 非SS / あはき / 適用徴収)
2. **業務タイプ** (新SS(W) / 新SS(片道) など)
3. **OCR区分** (OCR対象 / OCR非対象 / 目検)
4. **工程名** (エントリ1 / エントリ2 / 補正 / SV補正)

---

## 📊 データベースとの対応

### 現在のテーブル構造

```sql
-- 業務マスタ (businesses)
business_id VARCHAR(20)         -- 例: 523201 (新SS(W))
business_name VARCHAR(100)      -- 例: 新SS(W)
business_category VARCHAR(50)   -- 例: SS

-- 工程マスタ (processes)
business_id VARCHAR(20)         -- 外部キー
process_id VARCHAR(10)          -- 例: 152 (エントリ1)
process_name VARCHAR(100)       -- 例: エントリ1
process_category VARCHAR(50)    -- 例: OCR対象
```

### 階層を表現するクエリ例

```sql
SELECT
    b.business_category AS '大分類',
    b.business_name AS '業務タイプ',
    p.process_category AS 'OCR区分',
    p.process_name AS '工程名',
    p.business_id,
    p.process_id
FROM
    businesses b
    INNER JOIN processes p ON b.business_id = p.business_id
WHERE
    b.business_category = 'SS'
    AND b.business_name = '新SS(W)'
    AND p.process_category = 'OCR対象'
    AND p.process_name = 'エントリ1';
```

**結果**:
```
大分類: SS
業務タイプ: 新SS(W)
OCR区分: OCR対象
工程名: エントリ1
business_id: 523201
process_id: 152
```

---

## 🤖 AI応答の改善ポイント

### ❌ 現在の問題

現在のAI応答:
```
東京のエントリ1から2名を札幌へ配置転換することを提案します。
```

**問題点**:
- 「エントリ1」だけでは**どの業務のエントリ1か不明**
- SSなのか非SSなのか?
- OCR対象なのか非対象なのか?
- 新SS(W)なのか新SS(片道)なのか?

---

### ✅ 改善後の応答

```
「SS」の「新SS(W)」の「OCR対象」の「エントリ1」において、
東京から田中太郎さん、佐藤花子さんの2名を札幌へ配置転換することを提案します。

【詳細】
- 大分類: SS (社会保険)
- 業務タイプ: 新SS(W)
- OCR区分: OCR対象
- 工程: エントリ1

【配置転換内容】
- 移動元: 東京 (現在7名配置)
- 移動先: 札幌 (現在3名配置)
- 対象者: 田中太郎さん、佐藤花子さん

【期待効果】
- 札幌の生産性: +15%向上見込み
- 遅延削減: 約30分短縮
```

---

## 🔧 実装すべき変更

### 1. データベーススキーマの確認

現在の `processes` テーブルに以下が含まれているか確認:
- ✅ `business_id` - 業務タイプ識別
- ✅ `process_id` - 工程識別
- ✅ `process_name` - 工程名
- ✅ `process_category` - OCR区分

**結論**: 現在のスキーマで対応可能

---

### 2. AIプロンプトの修正

バックエンド (`aimee-be/app/services/integrated_llm_service.py`) で、
AI応答生成時に以下を含めるようプロンプトを修正:

```python
prompt = f"""
あなたは配置最適化AIアシスタントです。

【重要】配置提案時は、必ず以下の4階層を明示してください:
1. 大分類 (SS / 非SS / あはき / 適用徴収)
2. 業務タイプ (新SS(W) / 新SS(片道) など)
3. OCR区分 (OCR対象 / OCR非対象 / 目検)
4. 工程名 (エントリ1 / エントリ2 / 補正 / SV補正)

例: 「SS」の「新SS(W)」の「OCR対象」の「エントリ1」

【データベース情報】
{database_context}

【ユーザーの質問】
{user_message}
"""
```

---

### 3. データベース照会の強化

配置提案生成時に、以下の情報を取得:

```python
# 階層情報を含めた工程情報取得
query = """
SELECT
    b.business_category AS category,
    b.business_name AS business,
    p.process_category AS ocr_type,
    p.process_name AS process,
    COUNT(*) AS operator_count
FROM
    operators o
    JOIN operator_process_capabilities opc ON o.operator_id = opc.operator_id
    JOIN businesses b ON opc.business_id = b.business_id
    JOIN processes p ON opc.business_id = p.business_id AND opc.process_id = p.process_id
WHERE
    o.location_id = ?
GROUP BY
    b.business_category, b.business_name, p.process_category, p.process_name
"""
```

---

## 📅 作業予定

1. ✅ 業務階層構造の理解
2. ⏳ データベーススキーマの確認・修正
3. ⏳ AIプロンプトの修正
4. ⏳ バックエンドのデータ取得ロジック修正
5. ⏳ フロントエンドの表示形式修正
6. ⏳ テストデータ作成・投入
7. ⏳ 動作確認テスト

---

**作成日**: 2025-10-09
**最終更新**: 業務階層構造分析完了
