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
    StreamlitUI["Streamlit UI<br/>EC2: 43.207.175.35:8501<br/><br/>・チャット画面<br/>・提案カード表示"]

    %% ======== レイヤー3: API Client ========
    APIClient["API Client<br/><br/>・HTTP POST<br/>・JSON変換"]

    %% ======== レイヤー4: FastAPI ========
    FastAPI["FastAPI<br/>EC2: 54.150.242.233:8002<br/><br/>・非同期処理<br/>・ルーティング"]

    %% ======== レイヤー5: STEP 1 ========
    Step1["STEP 1: 意図解析 - 0.5秒<br/>入力: メッセージ<br/>出力: intent_type"]
    OllamaLight["Ollama Light qwen2:0.5b<br/>ポート: 11433"]

    %% ======== レイヤー6: STEP 2 ========
    Step2["STEP 2: RAG検索 - 0.3秒<br/>入力: メッセージ<br/>出力: 管理者ノウハウ3件"]
    ChromaDB["ChromaDB ポート: 8003<br/>・管理者ノウハウ: 12件<br/>・ベクトル検索"]

    %% ======== レイヤー7: STEP 3 ========
    Step3["STEP 3: DB照会 - 0.8秒<br/>入力: intent + entities<br/>出力: 進捗/オペレータ情報"]
    MySQL["MySQL RDS<br/>・progress_snapshots: 832件<br/>・operators: 100名"]

    %% ======== レイヤー8: STEP 4 ========
    Step4["STEP 4: 提案生成 - 0.2秒<br/>入力: DB Data + RAG<br/>出力: 配置変更案"]

    %% ======== レイヤー9: STEP 5 ========
    Step5["STEP 5: 応答生成 - 2.5秒<br/>入力: All Context<br/>出力: 日本語応答"]
    OllamaMain["Ollama Main gemma3:4b<br/>ポート: 11435"]

    %% ======== レイヤー10: 応答 ========
    Response["📤 応答<br/>response: 日本語応答文<br/>suggestion: 配置変更案<br/>impact: 効果予測"]

    %% ======== 垂直フロー（上から下へ） ========
    User --> StreamlitUI
    StreamlitUI --> APIClient
    APIClient --> FastAPI
    FastAPI --> Step1

    %% STEP 1の処理
    Step1 --> OllamaLight
    OllamaLight --> Step2

    %% STEP 2の処理
    Step2 --> ChromaDB
    ChromaDB --> Step3

    %% STEP 3の処理
    Step3 --> MySQL
    MySQL --> Step4

    %% STEP 4の処理
    Step4 --> Step5

    %% STEP 5の処理
    Step5 --> OllamaMain
    OllamaMain --> Response

    %% 応答の返却
    Response --> FastAPI
    FastAPI --> APIClient
    APIClient --> StreamlitUI
    StreamlitUI --> User

    %% スタイル定義
    classDef userStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:3px
    classDef frontendStyle fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef backendStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef stepStyle fill:#fff9c4,stroke:#f9a825,stroke-width:2px
    classDef aiStyle fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef dataStyle fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef responseStyle fill:#e0f7fa,stroke:#0097a7,stroke-width:3px

    class User userStyle
    class StreamlitUI,APIClient frontendStyle
    class FastAPI backendStyle
    class Step1,Step2,Step3,Step4,Step5 stepStyle
    class OllamaLight,OllamaMain aiStyle
    class ChromaDB,MySQL dataStyle
    class Response responseStyle
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

## 📊 処理時間の内訳

各ステップの処理時間（実測値）:

| ステップ | 処理内容 | 時間 |
|---------|---------|------|
| **STEP 1** | 意図解析（qwen2:0.5b） | 0.5秒 |
| **STEP 2** | RAG検索（ChromaDB） | 0.3秒 |
| **STEP 3** | DB照会（MySQL） | 0.8秒 |
| **STEP 4** | 提案生成（ロジック） | 0.2秒 |
| **STEP 5** | 応答生成（gemma3:4b） | 2.5秒 |
| **合計** | | **4.3秒** |

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
