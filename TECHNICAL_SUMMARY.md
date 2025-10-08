# AIMEE システム技術要素まとめ

## 📅 最終更新日
2025-10-08

---

## 🏗️ システム構成

### アーキテクチャ
```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │─────▶│   Backend    │─────▶│   MySQL DB  │
│ (Streamlit) │ HTTP │   (FastAPI)  │ SQL  │  (aimee_db) │
│  Port 8501  │      │   Port 8002  │      │  Port 3306  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├─────▶ Ollama Light (qwen2:0.5b) Port 11433
                            │       意図解析用
                            │
                            ├─────▶ Ollama Main (gemma3:4b) Port 11435
                            │       応答生成用
                            │
                            ├─────▶ ChromaDB Port 8003
                            │       RAG検索用
                            │
                            └─────▶ Redis Port 6380
                                    キャッシュ用
```

---

## 💻 技術スタック

### フロントエンド
- **フレームワーク**: Streamlit 1.28+
- **可視化**: Plotly 5.17+
- **データ処理**: Pandas 2.1+
- **HTTP通信**: requests 2.31+
- **コンテナ**: Docker (Dockerfile)

### バックエンド
- **フレームワーク**: FastAPI
- **非同期処理**: asyncio, httpx
- **DB接続**: SQLAlchemy (AsyncSession), aiomysql
- **LLM**: Ollama (ローカルモデル)
- **RAG**: ChromaDB (ベクトルDB)
- **キャッシュ**: Redis
- **コンテナ**: Docker Compose

### データベース
- **RDBMS**: MySQL 8.0
- **接続**: ローカルMySQL (host.docker.internal:3306)
- **ユーザー**: aimee_user / Aimee2024!
- **データベース名**: aimee_db

### AI/LLM
- **軽量モデル**: qwen2:0.5b (意図解析)
- **メインモデル**: gemma3:4b (応答生成)
- **推論エンジン**: Ollama
- **ベクトルDB**: ChromaDB
- **処理時間**: 5〜10秒

---

## 📊 主要機能の技術実装

### 1. アラート表示機能

#### 技術要素
- **データソース**: `login_records_by_location` テーブル
- **API**: `GET /api/v1/alerts/check`
- **処理**: AlertService.check_all_alerts()

#### アラート基準
```python
ALERT_THRESHOLDS = {
    "ss_massive_threshold": 1000,           # SS受領1000件以上
    "max_assignment_minutes": 60,           # 長時間配置60分以上
    "correction_threshold_shinagawa": 50,   # 品川補正50件以上
    "correction_threshold_osaka": 100,      # 大阪補正100件以上
    "entry_balance_threshold": 0.3,         # エントリバランス差30%以上
}
```

#### 現在表示されるアラート
1. **SS案件大量受領アラート** (critical)
   - 固定値: 1,269件
   - データソース: 固定値 (TODO: 実データから取得)

2. **長時間配置の検出** (medium)
   - 固定値: オペレータa1234567が90分配置
   - データソース: 固定値 (TODO: daily_assignmentsから取得)

#### タイムアウト設定
- フロントエンド: 120秒
- バックエンド: N/A (即時応答)

---

### 2. チャット・配置提案機能

#### 処理フロー
```
ユーザー入力
  ↓
【ステップ1】意図解析 (Ollama Light - qwen2:0.5b)
  - intent_type: delay_resolution / resource_allocation / status_check
  - urgency: high / medium / low
  - entities: location, process, issue_type
  処理時間: 約2秒
  ↓
【ステップ2】RAG検索 (ChromaDB)
  - セマンティック検索
  - 類似コンテキスト取得
  処理時間: 約0.5秒 (遅延初期化で初回のみ追加1秒)
  ↓
【ステップ3】データベース照会 (MySQL)
  - login_records_by_location から配置状況取得
  - 余剰人員・不足人員を分析
  処理時間: 約0.5秒
  ↓
【ステップ4】提案生成 (Python)
  - 余剰拠点から不足拠点へのマッチング
  - 最大3件の配置転換を生成
  処理時間: 約0.1秒
  ↓
【ステップ5】応答生成 (Ollama Main - gemma3:4b)
  - データを元に自然言語応答を生成
  処理時間: 約2〜3秒
  ↓
フロントエンドに返却
```

**合計処理時間**: 5〜10秒

#### 実データ使用状況
- ✅ **login_records_by_location**: 拠点別ログイン状況 (17件)
- ✅ **operators**: オペレータマスタ (10件、拠点割当済み)
- ⚠️ **daily_assignments**: 配置計画 (0件 - 未使用)
- ⚠️ **progress_snapshots**: 進捗スナップショット (0件 - 未使用)

#### 余剰・不足判定ロジック
```python
for loc_name, count in locations_data.items():
    if count >= 3:  # 3名以上 = 余剰
        surplus = count - 2  # 2名を残して余剰
    elif count == 1:  # 1名 = 不足
        shortage = 1  # 1名追加で2名に
```

#### マッチングロジック
```python
# 不足している拠点・工程に対して、同じ工程で余剰がある拠点から配置
for shortage in shortage_list:
    for resource in available_resources:
        if resource.process == shortage.process:  # 工程名一致
            if resource.location != shortage.location:  # 同一拠点除外
                → 配置転換案を生成
```

#### 配置提案の例
```json
{
  "id": "SGT20251008-130340",
  "changes": [
    {"from": "佐世保", "to": "札幌", "process": "エントリ1", "count": 1},
    {"from": "東京", "to": "札幌", "process": "エントリ2", "count": 1},
    {"from": "東京", "to": "札幌", "process": "補正", "count": 1}
  ],
  "impact": {
    "productivity": "+30%",
    "delay": "-45分",
    "quality": "維持"
  },
  "reason": "実データに基づく3名の配置調整",
  "confidence_score": 0.85
}
```

---

### 3. 承認機能

#### 技術要素
- **API**: `POST /api/v1/approvals/{approval_id}/action`
- **DB保存**: `approval_history` テーブル
- **データ形式**: JSON (changes, impact)

#### 承認履歴テーブル構造
```sql
CREATE TABLE approval_history (
    approval_history_id INT AUTO_INCREMENT PRIMARY KEY,
    suggestion_id VARCHAR(50) NOT NULL,
    changes JSON NOT NULL,
    impact JSON,
    action_type ENUM('approved', 'rejected', 'modified'),
    action_user VARCHAR(100),
    action_user_id VARCHAR(50),
    feedback_reason TEXT,
    feedback_notes TEXT,
    execution_status ENUM('pending', 'executing', 'completed', 'failed'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 承認フロー
```
ユーザーが「✅ 承認」をクリック
  ↓
api_client.execute_approval_action(approval_id, "approve", ...)
  ↓
POST /api/v1/approvals/{id}/action
  ↓
approval_historyテーブルにINSERT
  ↓
別アプリがSELECTで読み取り可能
```

---

## 🗄️ データベーステーブル一覧

### マスタテーブル
| テーブル名 | 用途 | データ件数 |
|-----------|------|-----------|
| `locations` | 拠点マスタ | 7件 (札幌、西梅田、本町東、沖縄、品川、佐世保、和歌山) |
| `businesses` | 業務マスタ | 5件以上 |
| `processes` | 工程マスタ | 10件以上 |
| `operators` | オペレータマスタ | 10件 (拠点割当済み) |
| `operator_process_capabilities` | スキル情報 | 7件 |

### トランザクションテーブル
| テーブル名 | 用途 | データ件数 | 使用状況 |
|-----------|------|-----------|---------|
| `login_records_by_location` | 拠点別ログイン状況 | 17件 | ✅ 使用中 |
| `progress_snapshots` | 進捗スナップショット | 0件 | ❌ 未使用 |
| `daily_assignments` | 配置計画 | 0件 | ❌ 未使用 |
| `operator_work_records` | 作業実績 | 0件 | ❌ 未使用 |
| `approval_history` | 承認履歴 | 2件 (サンプル) | ✅ 使用可能 |

---

## 🔌 API エンドポイント一覧

### アラート
| Method | Endpoint | 用途 | レスポンス時間 |
|--------|----------|------|--------------|
| GET | `/api/v1/alerts` | アラート一覧取得 | 即時 |
| GET | `/api/v1/alerts/check` | アラート基準チェック | 即時 |
| GET | `/api/v1/alerts/{id}` | アラート詳細 | 即時 |
| POST | `/api/v1/alerts/{id}/resolve` | アラート解消提案 | 10〜30秒 |

### チャット
| Method | Endpoint | 用途 | レスポンス時間 |
|--------|----------|------|--------------|
| POST | `/api/v1/chat/message` | AIチャット | 5〜10秒 |
| GET | `/api/v1/chat/history` | チャット履歴 | 即時 |

### 承認
| Method | Endpoint | 用途 | レスポンス時間 |
|--------|----------|------|--------------|
| GET | `/api/v1/approvals` | 承認待ち一覧 | 即時 |
| GET | `/api/v1/approvals/{id}` | 承認詳細 | 即時 |
| POST | `/api/v1/approvals/{id}/action` | 承認/却下実行 | 即時 |

### ステータス
| Method | Endpoint | 用途 |
|--------|----------|------|
| GET | `/api/v1/health` | ヘルスチェック |
| GET | `/api/v1/status` | システム状態 |

---

## 🐳 Docker構成

### コンテナ一覧
| コンテナ名 | イメージ | ポート | メモリ制限 | 用途 |
|-----------|---------|--------|-----------|------|
| `aimee-be-api-1` | aimee-be-api | 8002 | 2G | FastAPI |
| `aimee-be-ollama-light-1` | ollama/ollama:latest | 11433 | 3G | 軽量LLM |
| `aimee-be-ollama-main-1` | ollama/ollama:latest | 11435 | 12G | メインLLM |
| `aimee-be-chromadb-1` | chromadb/chroma:latest | 8003 | 1G | ベクトルDB |
| `aimee-be-redis-1` | redis:7-alpine | 6380 | 512M | キャッシュ |
| `aimee-frontend` | aimee-fe | 8501 | 1G | Streamlit |

### ポートマッピング
- **8002**: バックエンドAPI (FastAPI)
- **8003**: ChromaDB
- **8501**: フロントエンド (Streamlit)
- **3306**: MySQL (ローカル)
- **6380**: Redis
- **11433**: Ollama Light
- **11435**: Ollama Main

### 環境変数
```env
# バックエンド (.env)
PORT=8002
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@host.docker.internal:3306/aimee_db
OLLAMA_LIGHT_HOST=ollama-light
OLLAMA_MAIN_HOST=ollama-main
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
CHROMADB_EXTERNAL_PORT=8003

# フロントエンド
AIMEE_API_URL=http://host.docker.internal:8002
```

---

## 🤖 AI/LLM処理詳細

### Ollama モデル

#### qwen2:0.5b (軽量モデル)
- **用途**: 意図解析
- **パラメータ数**: 494M
- **量子化**: Q4_0
- **処理時間**: 1〜2秒
- **設定**:
  ```python
  temperature: 0.1
  num_predict: 200
  top_k: 10
  top_p: 0.9
  ```

#### gemma3:4b (メインモデル)
- **用途**: 応答生成
- **パラメータ数**: 4B
- **処理時間**: 2〜3秒
- **設定**:
  ```python
  temperature: 0.7
  num_predict: 200
  top_k: 20
  top_p: 0.8
  ```

### ChromaDB (RAG)
- **コレクション名**: aimee_knowledge
- **用途**: セマンティック検索、過去事例検索
- **初期化**: 遅延初期化 (初回使用時)
- **検索結果数**: n_results=3
- **現在の状態**: 初期化成功、データ0件

---

## 📁 プロジェクト構造

```
/Users/umemiya/Desktop/erax/
├── aimee-fe/                        # フロントエンド
│   ├── frontend/
│   │   ├── app.py                   # メインアプリ
│   │   └── src/
│   │       └── utils/
│   │           └── api_client.py    # API連携クライアント
│   ├── Dockerfile                   # フロントエンドDocker
│   ├── docker-compose.yml           # フロントエンドCompose
│   ├── requirements.txt             # Python依存関係
│   ├── docker-start-all.sh          # 全体起動スクリプト
│   ├── docker-stop-all.sh           # 全体停止スクリプト
│   ├── docker-check-status.sh       # 状態確認スクリプト
│   ├── CLAUDE.md                    # プロジェクト情報
│   ├── INTEGRATION.md               # 統合ガイド
│   ├── COMPLETE.md                  # 完了作業記録
│   └── README.md                    # クイックスタート
│
├── aimee-be/                        # バックエンド
│   ├── app/
│   │   ├── main.py                  # FastAPIアプリ
│   │   ├── api/v1/endpoints/
│   │   │   ├── alerts.py            # アラートエンドポイント
│   │   │   ├── chat.py              # チャットエンドポイント
│   │   │   └── approvals.py         # 承認エンドポイント
│   │   ├── services/
│   │   │   ├── integrated_llm_service.py  # 統合LLMサービス
│   │   │   ├── ollama_service.py          # Ollama連携
│   │   │   ├── chroma_service.py          # ChromaDB連携
│   │   │   ├── database_service.py        # DB照会
│   │   │   └── alert_service.py           # アラート判定
│   │   ├── schemas/                 # Pydanticスキーマ
│   │   └── db/session.py            # DB接続
│   ├── Dockerfile.api               # バックエンドDocker
│   ├── docker-compose.yml           # バックエンドCompose
│   ├── .env                         # 環境変数
│   └── start.py                     # ローカル起動スクリプト
│
└── aimee-db/                        # データベース
    ├── config.py                    # DB接続設定
    ├── schema.sql                   # テーブル定義
    ├── approval_history_table.sql   # 承認履歴テーブル
    ├── import_*.py                  # データインポートスクリプト
    └── 資料/ (別フォルダ参照)       # 実データCSV
```

---

## 🔄 起動・停止コマンド

### Docker起動 (推奨)
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 全体起動
./docker-start-all.sh

# 個別起動
./docker-start-backend.sh   # バックエンドのみ
./docker-start-frontend.sh  # フロントエンドのみ

# 状態確認
./docker-check-status.sh

# 停止
./docker-stop-all.sh
```

### ローカル起動 (開発用)
```bash
# バックエンド
cd /Users/umemiya/Desktop/erax/aimee-be
python3 start.py

# フロントエンド
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
streamlit run app.py
```

### コンテナ個別操作
```bash
cd /Users/umemiya/Desktop/erax/aimee-be

# 全コンテナ起動
docker-compose up -d

# APIのみ再起動
docker-compose restart api

# Ollamaのみ起動
docker-compose up -d ollama-light ollama-main

# ログ確認
docker-compose logs -f api
docker-compose logs -f frontend
```

---

## 🐛 トラブルシューティング

### アラートが表示されない
```bash
# バックエンド起動確認
curl http://localhost:8002/api/v1/alerts/check

# ログ確認
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose logs -f api | grep -i alert
```

### チャットが遅い・タイムアウト
- **原因**: Ollama処理が重い (ローカルLLM)
- **対策**: タイムアウトを180秒に設定済み
- **確認**:
```bash
# Ollama動作確認
curl http://localhost:11433/api/tags
curl http://localhost:11435/api/tags

# モデル確認
docker exec aimee-be-ollama-light-1 ollama list
docker exec aimee-be-ollama-main-1 ollama list
```

### 配置提案が生成されない
- **原因**: DBデータ不足
- **確認**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as count FROM login_records_by_location')
print(f\"login_records: {result[0]['count']}件\")
"
```

### ChromaDB初期化が遅い
- **対策**: 遅延初期化実装済み
- **初回のみ**: 1秒追加
- **2回目以降**: キャッシュ使用

### MySQL接続エラー
- **docker-compose環境変数**: `host.docker.internal:3306` に設定済み
- **確認**:
```bash
# ローカルMySQL起動確認
mysql.server status

# 接続テスト
mysql -u aimee_user -p'Aimee2024!' aimee_db -e "SELECT 1"
```

### ポート競合
```bash
# ポート使用確認
lsof -i:8002  # バックエンドAPI
lsof -i:8003  # ChromaDB
lsof -i:8501  # フロントエンド
lsof -i:3306  # MySQL

# プロセスkill
kill -9 $(lsof -ti:8002)
```

---

## ⚙️ 設定ファイル詳細

### バックエンド (.env)
```env
# アプリケーション
APP_NAME=AIMEE-Backend
APP_VERSION=1.0.0
PORT=8002

# データベース
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@localhost:3306/aimee_db

# LLM
OLLAMA_LIGHT_HOST=localhost
OLLAMA_LIGHT_PORT=11433
INTENT_MODEL=qwen2:0.5b

OLLAMA_MAIN_HOST=localhost
OLLAMA_MAIN_PORT=11435
MAIN_MODEL=gemma3:4b

# ChromaDB
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
CHROMADB_EXTERNAL_PORT=8003

# Redis
REDIS_URL=redis://redis:6379/0
```

### フロントエンド (api_client.py)
```python
self.base_url = os.getenv("AIMEE_API_URL", "http://localhost:8002")

# タイムアウト設定
check_alerts: timeout=120秒
chat_with_ai: timeout=180秒
```

### Docker Compose (バックエンド)
```yaml
services:
  api:
    ports: ["8002:8002"]
    environment:
      DATABASE_URL: mysql+aiomysql://aimee_user:Aimee2024!@host.docker.internal:3306/aimee_db
      OLLAMA_LIGHT_HOST: ollama-light
      OLLAMA_MAIN_HOST: ollama-main
    extra_hosts:
      - "host.docker.internal:host-gateway"
    depends_on:
      - redis
      - ollama-light
      - ollama-main
      - chromadb
```

---

## 📈 パフォーマンス最適化

### 実施済み最適化
1. **ChromaDB遅延初期化**: 初回使用時のみ初期化 (1秒削減)
2. **意図解析軽量化**: qwen2:0.5b使用 (高速)
3. **DBクエリ最適化**: 最新スナップショットのみ取得
4. **同一拠点除外**: 無意味な配置転換を除外

### 処理時間内訳
```
意図解析 (Ollama Light):     2秒
RAG検索 (ChromaDB):           0.5秒
DB照会 (MySQL):               0.5秒
提案生成 (Python):            0.1秒
応答生成 (Ollama Main):       2〜3秒
─────────────────────────────────
合計:                         5〜10秒
```

---

## 🔒 セキュリティ

### 認証
- **現状**: 認証なし (ローカル開発環境)
- **今後**: JWT認証実装予定

### データベース
- **接続**: ユーザー/パスワード認証
- **通信**: ローカルのみ
- **個人情報**: オペレータ名を含む (暗号化なし)

---

## 📝 制限事項・既知の問題

### 現在の制限
1. **データ件数が少ない**
   - login_records: 17件のみ
   - operators: 10件のみ
   - 実運用には数千〜数万件必要

2. **リアルタイムデータ未対応**
   - progress_snapshots: 0件
   - daily_assignments: 0件
   - 手動でCSVインポートが必要

3. **認証機能なし**
   - ユーザー管理未実装
   - 承認者の識別が固定値

4. **通知機能未実装**
   - WebSocket未使用
   - リアルタイム通知なし

### 既知の問題
1. **ChromaDB初期化が遅い** → 遅延初期化で対応済み
2. **Ollamaが重い** → ローカルLLMのため仕方ない (5〜10秒)
3. **MySQLコンテナが起動しない** → ローカルMySQL使用で回避済み
4. **ポート競合 (8002)** → ChromaDBを8003に変更済み

---

## 🚀 今後の拡張

### Phase 2
1. **実データの完全投入**
   - progress_snapshots (進捗情報)
   - daily_assignments (配置計画)
   - operator_work_records (作業実績)

2. **RAGデータ蓄積**
   - 承認履歴をChromaDBに保存
   - 過去の成功事例を学習

3. **リアルタイム更新**
   - 2分間隔でデータポーリング
   - WebSocket通知

### Phase 3
1. **認証・権限管理**
   - ユーザーログイン
   - 拠点別権限

2. **高度な最適化**
   - 数理最適化アルゴリズム
   - 予測モデル (XGBoost)

3. **外部システム連携**
   - RealWorks連携
   - 自動データ取得

---

## 📚 参考資料

- **要件定義書**: `01_requirements/requirements.md`
- **DB設計書**: `02_database/design/02_table_specifications.md`
- **統合ガイド**: `INTEGRATION.md`
- **完了作業**: `COMPLETE.md`
- **システム構成図**: [diagrams.net](https://app.diagrams.net/?splash=0#G1kBIJvslm_yRlK2QyCbrDwr9GZnJFTb3X)
- **全体概要**: [Notion](https://pouncing-attic-dd0.notion.site/24154d8b9bc0807c8dfbc7278e5655cf)

---

**作成日**: 2025-10-08
**最終更新**: 実データ配置転換提案生成完了時点
