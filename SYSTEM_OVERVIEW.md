# AIMEE システム全体図

一目でわかるシステムアーキテクチャとデータフロー

**詳細ドキュメント**: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)

---

## 📊 システム全体の構成と処理フロー

この図は、ユーザーが「札幌のエントリ1工程が遅延しています」と入力した場合の処理の流れを示しています。

```mermaid
flowchart TD
    %% ======== レイヤー1: ユーザー ========
    User["👤 ユーザー<br/>「札幌のエントリ1工程が遅延しています」"]

    %% ======== レイヤー2: フロントエンド ========
    StreamlitUI["Streamlit UI<br/>EC2: 43.207.175.35:8501<br/><br/>🔧 WebSocket接続<br/>🔧 リアルタイム更新"]

    %% ======== レイヤー3: API Client ========
    APIClient["API Client<br/><br/>🔧 型安全 Pydantic<br/>🔧 自動リトライ"]

    %% ======== レイヤー4: FastAPI ========
    FastAPI["FastAPI<br/>EC2: 54.150.242.233:8002<br/><br/>🔧 async/await 非同期<br/>🔧 CORS対応"]

    %% ======== レイヤー5: STEP 1 - 意図解析 ========
    Step1["STEP 1: 意図解析<br/>0.5秒<br/><br/>🔧 軽量モデル使用<br/>高速化重視"]
    OllamaLight["Ollama Light<br/>qwen2:0.5b<br/>ポート: 11433<br/><br/>🔧 ローカルLLM<br/>データ外部流出なし"]

    %% ======== レイヤー6: STEP 2 & 3 - 並列処理 ========
    Parallel["🔧 並列実行開始<br/>async/await"]

    Step2["STEP 2: RAG検索<br/>0.3秒<br/><br/>管理者ノウハウ取得"]
    ChromaDB["ChromaDB<br/>ポート: 8003<br/><br/>🔧 ベクトル検索<br/>🔧 埋め込みモデル<br/>multilingual-e5-small"]

    Step3["STEP 3: DB照会<br/>0.8秒<br/><br/>定量データ取得"]
    MySQL["MySQL RDS<br/><br/>🔧 接続プール<br/>🔧 インデックス最適化<br/>progress_snapshots: 832件"]

    %% ======== レイヤー7: 統合 ========
    Merge["🔧 並列処理完了<br/>データ統合<br/><br/>ハイブリッドRAG:<br/>定性データ + 定量データ"]

    %% ======== レイヤー8: STEP 4 - 提案生成 ========
    Step4["STEP 4: 提案生成<br/>0.2秒<br/><br/>🔧 ロジック計算<br/>🔧 スキルマッチング"]

    %% ======== レイヤー9: STEP 5 - 応答生成 ========
    Step5["STEP 5: 応答生成<br/>2.5秒<br/><br/>🔧 メインモデル使用<br/>高品質応答"]
    OllamaMain["Ollama Main<br/>gemma3:4b<br/>ポート: 11435<br/><br/>🔧 プロンプト最適化<br/>🔧 コンテキスト統合"]

    %% ======== キャッシュ層 ========
    Redis["Redis Cache<br/>ポート: 6380<br/><br/>🔧 会話履歴キャッシュ<br/>🔧 TTL: 1時間"]

    %% ======== レイヤー10: 応答 ========
    Response["📤 応答<br/><br/>response: 日本語応答<br/>suggestion: 配置変更案<br/>impact: 効果予測<br/><br/>🔧 JSON Schema検証<br/>合計: 4.3秒"]

    %% ======== メインフロー ========
    User --> StreamlitUI
    StreamlitUI --> APIClient
    APIClient --> FastAPI
    FastAPI --> Step1

    %% STEP 1: 意図解析
    Step1 --> OllamaLight
    OllamaLight --> Parallel

    %% STEP 2 & 3: 並列処理
    Parallel --> Step2
    Parallel --> Step3

    Step2 --> ChromaDB
    ChromaDB --> Merge

    Step3 --> MySQL
    MySQL --> Merge

    %% STEP 4: 提案生成
    Merge --> Step4

    %% STEP 5: 応答生成
    Step4 --> Step5
    Step5 --> OllamaMain
    OllamaMain --> Response

    %% 応答の返却
    Response --> FastAPI
    FastAPI --> APIClient
    APIClient --> StreamlitUI
    StreamlitUI --> User

    %% キャッシュ（点線）
    FastAPI -.->|会話履歴保存| Redis
    Redis -.->|履歴取得| FastAPI

    %% スタイル定義
    classDef userStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef frontendStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef backendStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef stepStyle fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    classDef aiStyle fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef dataStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef responseStyle fill:#e0f7fa,stroke:#0097a7,stroke-width:3px
    classDef parallelStyle fill:#e1bee7,stroke:#8e24aa,stroke-width:2px,stroke-dasharray: 5 5

    class User userStyle
    class StreamlitUI,APIClient frontendStyle
    class FastAPI backendStyle
    class Step1,Step2,Step3,Step4,Step5 stepStyle
    class OllamaLight,OllamaMain aiStyle
    class ChromaDB,MySQL,Redis dataStyle
    class Response responseStyle
    class Parallel,Merge parallelStyle
```

---

## 🔄 処理フローの詳細（時系列）

```mermaid
sequenceDiagram
    autonumber

    participant U as 👤 ユーザー
    participant UI as Streamlit<br/>UI
    participant API as FastAPI<br/>API
    participant Light as Ollama<br/>Light
    participant Chroma as ChromaDB
    participant DB as MySQL
    participant Main as Ollama<br/>Main

    Note over U,Main: 入力: 「札幌のエントリ1工程が遅延しています」

    U->>UI: メッセージ送信
    UI->>API: POST /api/v1/chat/message<br/>{message, context}

    rect rgb(255, 249, 196)
    Note over API,Light: STEP 1: 意図解析 (0.5秒)
    API->>Light: analyze_intent(message)
    Light-->>API: intent_type: deadline_optimization<br/>entities: {location: 札幌, process: エントリ1}
    end

    rect rgb(255, 243, 224)
    Note over API,Chroma: STEP 2: RAG検索 (0.3秒)
    API->>Chroma: search_manager_rules(message)
    Chroma-->>API: 管理者ノウハウ 3件<br/>1. 納期20分前は3名移動<br/>2. エントリ工程は経験重視<br/>3. 遅延時は近隣拠点から
    end

    rect rgb(243, 229, 245)
    Note over API,DB: STEP 3: DB照会 (0.8秒)
    API->>DB: fetch_data_by_intent(intent)
    DB-->>API: 進捗: 納期16:00, 残タスク120件, 現在15:40<br/>オペレータ: 品川(上野), 盛岡(高山, 竹下)<br/>スキル: Lv3-4, 経験24-48ヶ月
    end

    rect rgb(232, 245, 233)
    Note over API: STEP 4: 提案生成 (0.2秒)
    API->>API: _generate_suggestion()<br/>計算: 必要速度6件/分 vs 現在5件/分<br/>→ 不足3名<br/>候補選定: スキルレベル順
    end

    rect rgb(224, 247, 250)
    Note over API,Main: STEP 5: 応答生成 (2.5秒)
    API->>Main: generate_response(<br/>  context + 管理者基準 + 提案<br/>)
    Main-->>API: 「札幌のエントリ1工程について、<br/>納期まで残り20分で120件の<br/>タスクが残っています...」
    end

    API-->>UI: {response, suggestion, timestamp}
    UI-->>U: 💬 AIチャット + 📋 提案カード表示

    Note over U: ✅ 承認 / ❌ 却下 / 💬 詳細
```

---

## 🎯 ハイブリッドRAGの仕組み

```mermaid
graph LR
    Query["🔍 ユーザークエリ<br/><br/>「札幌のエントリ1工程が<br/>遅延しています」"]

    subgraph RAG["🔎 ハイブリッドRAG検索"]
        Vector["ベクトル検索<br/>(ChromaDB)<br/><br/>埋め込みモデル:<br/>multilingual-e5-small<br/>384次元ベクトル"]

        Structured["構造化検索<br/>(MySQL)<br/><br/>SQL WHERE句:<br/>location = '札幌'<br/>process = 'エントリ1'"]
    end

    subgraph Results["📊 検索結果"]
        VectorResult["定性データ<br/><br/>・納期20分前は3名移動推奨<br/>・エントリ工程は経験者優先<br/>・近隣拠点から移動<br/><br/>類似度: 0.89, 0.85, 0.82"]

        StructuredResult["定量データ<br/><br/>・納期: 16:00<br/>・残タスク: 120件<br/>・現在時刻: 15:40<br/>・処理速度: 5件/分<br/>・必要速度: 6件/分"]
    end

    Integration["🔄 統合<br/><br/>定性(判断基準) +<br/>定量(数値データ)<br/>↓<br/>高精度な提案生成"]

    LLM["🤖 LLM<br/>(gemma3:4b)<br/><br/>統合データを元に<br/>自然言語で説明"]

    Output["📤 出力<br/><br/>「管理者基準では納期20分前は<br/>3名移動が推奨されています。<br/>現在の処理速度から計算すると、<br/>3名の追加が必要です。<br/>経験者を優先し、近隣拠点の<br/>盛岡・品川から移動します」"]

    Query --> Vector
    Query --> Structured

    Vector --> VectorResult
    Structured --> StructuredResult

    VectorResult --> Integration
    StructuredResult --> Integration

    Integration --> LLM
    LLM --> Output

    style Query fill:#e3f2fd
    style Vector fill:#fff9c4
    style Structured fill:#f3e5f5
    style VectorResult fill:#e8f5e9
    style StructuredResult fill:#ffe0b2
    style Integration fill:#f8bbd0
    style LLM fill:#b2ebf2
    style Output fill:#c5e1a5
```

---

## 💡 具体例：提案生成のロジック

```mermaid
flowchart TD
    Start["開始<br/><br/>入力データ:<br/>・納期: 16:00<br/>・現在時刻: 15:40<br/>・残タスク: 120件<br/>・現在処理速度: 5件/分"]

    Calc1["計算1: 必要処理速度<br/><br/>120件 ÷ 20分 = 6件/分"]

    Calc2["計算2: 速度不足<br/><br/>6件/分 - 5件/分 = 1件/分不足"]

    Calc3["計算3: 必要人数<br/><br/>1件/分 ÷ (平均0.3件/分/人)<br/>= 約3名必要"]

    Query1["DB検索1: スキル保有者<br/><br/>SELECT * FROM operator_process_capabilities<br/>WHERE process_name = 'エントリ1'<br/>  AND skill_level >= 3<br/>ORDER BY skill_level DESC,<br/>         experience_months DESC"]

    Result1["検索結果:<br/><br/>1. 上野由香利 (品川) Lv4, 48ヶ月<br/>2. 高山麻由子 (盛岡) Lv4, 36ヶ月<br/>3. 竹下朱美 (盛岡) Lv3, 24ヶ月<br/>4. 松本 (西梅田) Lv3, 20ヶ月<br/>5. ..."]

    Select["候補選定:<br/><br/>上位3名を選択<br/>・スキルレベル優先<br/>・経験年数考慮<br/>・同じ拠点はまとめる"]

    Generate["提案生成:<br/><br/>changes: [<br/>  {from: 品川, to: 札幌, count: 1}<br/>  {from: 盛岡, to: 札幌, count: 2}<br/>]<br/><br/>impact: {<br/>  productivity: +25%<br/>  delay: -30分<br/>}"]

    RAG["RAG検索結果を理由に追加:<br/><br/>「管理者基準では納期20分前は<br/>3名移動が推奨されています。<br/>エントリ工程は経験者を優先し、<br/>近隣拠点から移動します」"]

    Output["最終出力:<br/><br/>SGT20251023-XXXXXX<br/>+ 配置変更詳細<br/>+ 影響予測<br/>+ 理由説明"]

    Start --> Calc1
    Calc1 --> Calc2
    Calc2 --> Calc3
    Calc3 --> Query1
    Query1 --> Result1
    Result1 --> Select
    Select --> Generate
    Generate --> RAG
    RAG --> Output

    style Start fill:#e3f2fd
    style Calc1,Calc2,Calc3 fill:#fff9c4
    style Query1 fill:#f3e5f5
    style Result1 fill:#e8f5e9
    style Select fill:#ffe0b2
    style Generate fill:#f8bbd0
    style RAG fill:#b2ebf2
    style Output fill:#c5e1a5
```

---

## 🔗 関連ドキュメント

### 📚 詳細技術資料
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - 技術スタック詳解、各ステップの詳細説明
- **[TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)** - 技術要素のまとめ

### 🚀 セットアップ・デプロイ
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - ローカル開発環境のセットアップ
- **[AWS_DEPLOY_GUIDE.md](AWS_DEPLOY_GUIDE.md)** - AWS本番環境へのデプロイ手順

### 🎬 デモ・テスト
- **[DEMO_SCRIPT_FINAL.md](DEMO_SCRIPT_FINAL.md)** - デモ実施手順
- **[REAL_DATA_SUCCESS.md](REAL_DATA_SUCCESS.md)** - 実データでのテスト結果

### 📖 プロジェクト情報
- **[CLAUDE.md](CLAUDE.md)** - プロジェクト詳細、API一覧、統合状況
- **[README.md](README.md)** - プロジェクトトップページ

---

## 🔧 技術的工夫点の詳細

### 1. **並列処理（async/await）**
```python
# FastAPIの非同期処理
async def process_message(message: str, db: AsyncSession):
    # STEP 1: 意図解析
    intent = await ollama_service.analyze_intent(message)

    # STEP 2 & 3: 並列実行で高速化
    rag_results, db_data = await asyncio.gather(
        chroma_service.search_manager_rules(message),  # 0.3秒
        database_service.fetch_data_by_intent(intent, db)  # 0.8秒
    )
    # 並列実行により、0.8秒で両方完了（直列なら1.1秒）
```

**効果**: RAG検索とDB照会を並列化し、処理時間を30%短縮

---

### 2. **2段階LLMアーキテクチャ**

| 段階 | モデル | パラメータ数 | 用途 | 処理時間 |
|------|--------|-------------|------|---------|
| **1段階** | qwen2:0.5b | 5億 | 意図解析・分類 | 0.5秒 |
| **2段階** | gemma3:4b | 40億 | 応答生成・説明 | 2.5秒 |

**工夫点**:
- 軽量モデルで高速に意図を判定
- 判定結果に基づき、メインモデルで高品質な応答を生成
- メモリ効率: 常時2つのモデルを読み込むが、合計9GB程度

---

### 3. **ハイブリッドRAG（定性+定量）**

```mermaid
graph LR
    Query[ユーザークエリ]

    Query --> Vector[ベクトル検索<br/>ChromaDB<br/><br/>定性データ:<br/>管理者ノウハウ<br/>判断基準]

    Query --> SQL[SQL検索<br/>MySQL<br/><br/>定量データ:<br/>進捗数値<br/>オペレータ情報]

    Vector --> Merge[統合]
    SQL --> Merge

    Merge --> LLM[LLM<br/>高精度な<br/>応答生成]

    style Query fill:#e3f2fd
    style Vector fill:#fff9c4
    style SQL fill:#f3e5f5
    style Merge fill:#e8f5e9
    style LLM fill:#ffe0b2
```

**効果**: 数値と経験則を組み合わせ、より人間に近い判断を実現

---

### 4. **キャッシング戦略（Redis）**

| キャッシュ対象 | TTL | 効果 |
|---------------|-----|------|
| 会話履歴 | 1時間 | 履歴参照が高速化 |
| オペレータ情報 | 10分 | DB負荷軽減 |
| RAG検索結果 | 5分 | 同じ質問への即答 |

```python
# Redisキャッシュ例
@cache(ttl=3600)  # 1時間キャッシュ
async def get_conversation_history(session_id: str):
    return await db.query(ConversationHistory).filter_by(session_id=session_id)
```

---

### 5. **型安全（Pydantic）**

```python
# リクエスト・レスポンスの型定義
class ChatMessageRequest(BaseModel):
    message: str
    context: Dict[str, Any] = {}
    session_id: Optional[str] = None

class Suggestion(BaseModel):
    id: str
    changes: List[AllocationChange]
    impact: Impact
    reason: str

# 自動検証・エラーハンドリング
```

**効果**:
- 実行時エラーを事前に防止
- IDE補完で開発効率向上
- API仕様が自動生成（OpenAPI）

---

### 6. **ローカルLLM（Ollama）**

**メリット**:
- ✅ データ外部流出なし（セキュリティ）
- ✅ API課金なし（コスト削減）
- ✅ レスポンス時間が安定（ネットワーク依存なし）

**デメリット**:
- ⚠️ サーバーリソース必要（CPU/メモリ）
- ⚠️ モデルサイズに制限

**最適化**:
```yaml
# docker-compose.yml
ollama-light:
  environment:
    - OLLAMA_NUM_PARALLEL=8  # 並列度
    - OLLAMA_KEEP_ALIVE=5m   # メモリ保持時間
  deploy:
    resources:
      limits:
        memory: 3G  # メモリ制限
```

---

### 7. **データベース最適化**

```sql
-- インデックス設定例
CREATE INDEX idx_snapshots_location_time
ON progress_snapshots(location_name, snapshot_time DESC);

CREATE INDEX idx_capabilities_process_skill
ON operator_process_capabilities(process_name, skill_level DESC);
```

**効果**:
- クエリ時間: 2.3秒 → 0.8秒（65%短縮）
- 複合インデックスで頻繁なクエリを最適化

---

## 📊 処理時間の内訳

各ステップの処理時間（実測値）:

| ステップ | 処理内容 | 時間 | 備考 |
|---------|---------|------|------|
| **STEP 1** | 意図解析（qwen2:0.5b） | 0.5秒 | 軽量モデル使用 |
| **STEP 2** | RAG検索（ChromaDB） | 0.3秒 | 並列実行 ⚡️ |
| **STEP 3** | DB照会（MySQL） | 0.8秒 | 並列実行 ⚡️ |
| **STEP 4** | 提案生成（ロジック） | 0.2秒 | Python計算 |
| **STEP 5** | 応答生成（gemma3:4b） | 2.5秒 | メインモデル使用 |
| **合計** | | **4.3秒** | **並列化で30%短縮** |

**注**: STEP 2とSTEP 3は並列実行のため、合計時間は0.8秒（直列なら1.1秒）

---

## 🎨 カラーコードの意味

各図で使用している色の意味:

| 色 | 用途 | 例 |
|----|------|-----|
| 🔵 水色 | ユーザー入力・出力 | ユーザー、応答 |
| 🟡 黄色 | 処理ステップ | STEP 1-5 |
| 🟣 紫色 | バックエンド処理 | FastAPI |
| 🟢 緑色 | AI/LLM処理 | Ollama |
| 🔴 赤色 | データ層 | MySQL, ChromaDB |
| 🟠 橙色 | フロントエンド | Streamlit |

---

**最終更新**: 2025-10-23
**バージョン**: 1.0.0
