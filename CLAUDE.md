# AIMEE プロジェクト情報（AI用コンテキスト）

**最終更新**: 2025-11-01
**バージョン**: 2.0.0

## ⚠️ プロジェクトルール（重要）

### 1. ドキュメント管理ルール

**✅ 原則**: **新しいドキュメントを作らず、既存のものを上書きする**

- 新機能実装やバグ修正の際、新しいMarkdownファイルを作成しない
- 既存のマスタードキュメントを更新する
- 追記が必要な場合は、既存ドキュメントの該当セクションに追記

**マスタードキュメント（上書き対象）**:
1. **[README.md](README.md)** - プロジェクト概要、クイックスタート
2. **[CLAUDE.md](CLAUDE.md)** - このファイル（AI用コンテキスト）
3. **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - システムアーキテクチャ、技術解説
4. **[INTENT_TYPES.md](docs/INTENT_TYPES.md)** - 9分類の詳細、内部ロジック
5. **[DATABASE_SETUP.md](docs/DATABASE_SETUP.md)** - DBセットアップ、データ投入方法
6. **[LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)** - ローカル起動方法
7. **[AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md)** - AWSデプロイ方法

**例外**: 以下の場合のみ新規ドキュメント作成を許可
- 重要なバグ報告書（docs/に追加）
- 新機能の要件分析（docs/に追加）

---

### 2. 対応ログへの追記ルール

**✅ 原則**: **何か対応するたびにCHANGELOG.mdに追記する**

- バグ修正、機能追加、データ修正を行った際は必ず記録
- IMPLEMENTATION_LOG.mdは大規模な実装のみ
- CHANGELOG.mdは日常的な対応を記録

**記録すべき内容**:
- 問題・背景
- 対応内容
- 修正ファイル
- テスト結果
- 影響範囲

**記録フォーマット**:
```markdown
### YYYY-MM-DD HH:MM - [カテゴリ] タイトル

**問題・背景**: ...
**対応内容**: ...
**修正ファイル**: ...
**テスト結果**: ...
**影響範囲**: ...
```

**カテゴリ例**:
- [バグ修正]
- [機能追加]
- [データ修正]
- [パフォーマンス]
- [ドキュメント]

**参照**: [CHANGELOG.md](docs/CHANGELOG.md)

---

### 3. データベース管理ルール

**✅ 原則**: **データベースの挿入データを常に正しく保つ**

#### 必須確認事項

**開発・テスト時**:
1. ローカルDBの状態を常に確認
   ```bash
   cd /Users/umemiya/Desktop/erax/aimee-db
   python3 -c "
   from config import db_manager
   tables = ['operators', 'operator_process_capabilities', 'progress_snapshots']
   for t in tables:
       result = db_manager.execute_query(f'SELECT COUNT(*) as c FROM {t};')
       print(f'{t}: {result[0][\"c\"]}件')
   "
   ```

2. 期待値との照合
   - operators: 100件（モック名）
   - operator_process_capabilities: 191件
   - progress_snapshots: 832件

3. データ不足時は即座に投入
   ```bash
   # progress_snapshotsが0件の場合
   cd /Users/umemiya/Desktop/erax/aimee-db
   python3 extract_and_import_snapshots.py

   # ChromaDBが空の場合
   python3 import_manager_knowledge_to_chroma.py
   ```

**本番環境（AWS RDS）デプロイ時**:
1. RDSの状態を確認
   ```bash
   ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
       "docker exec aimee-be-mysql-1 mysql -u admin -p'Aimee2024!RDS' \
       -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
       aimee_db -e 'SELECT COUNT(*) FROM operators;'"
   ```

2. データ投入が必要な場合
   ```bash
   # モック名データ投入
   mysql -u admin -p'Aimee2024!RDS' \
       -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
       aimee_db < real_data_with_mock_names.sql
   ```

#### データ整合性チェック

**実装後・デプロイ後の必須確認**:
- [ ] operators テーブルに100件のデータがあるか
- [ ] operator_process_capabilities に191件のデータがあるか
- [ ] progress_snapshots に832件のデータがあるか
- [ ] ChromaDB に aimee_knowledge コレクション（12件）があるか
- [ ] approval_history テーブルが存在するか

**データ不足時の影響**:
- APIが「現在のリソースで対応可能です」しか返さない
- 配置提案が生成されない
- テスト精度が低下

**⚠️ 重要な注意事項**:
- **実名2,664名のデータは現在存在しない**
- 01_real_data_only.sqlはスキーマのみ（実データ含まず）
- 実際に使用可能なのは**モック100名**（real_data_with_mock_names.sql）のみ

**詳細**: [../aimee-db/DATABASE_STATUS.md](../aimee-db/DATABASE_STATUS.md) を参照

---

## プロジェクト概要

**プロジェクト名**: AIMEE (AI配置最適化システム)
**目的**: トランスコスモス様の健保組合業務における人員配置を、AI技術を活用して自動化・効率化

### リポジトリ構成
- **aimee-fe** (`/Users/umemiya/Desktop/erax/aimee-fe`): フロントエンド (Streamlit)
- **aimee-be** (`/Users/umemiya/Desktop/erax/aimee-be`): バックエンド (FastAPI)
- **aimee-db** (`/Users/umemiya/Desktop/erax/aimee-db`): データベース設定・スクリプト

---

## 📍 アクセスURL

### ローカル開発環境
- **フロントエンド**: http://localhost:8501
- **バックエンドAPI**: http://localhost:8002/docs
- **DB接続**: MySQL localhost:3306 (user: aimee_user, pass: Aimee2024!)

### 🌐 本番環境（AWS）
- **フロントエンド**: http://43.207.175.35:8501
- **バックエンドAPI**: http://54.150.242.233:8002
- **APIドキュメント**: http://54.150.242.233:8002/docs
- **データベース**: AWS RDS MySQL

---

## 🎉 最新の実装状況 (2025-10-20完了)

### データベース投入済み

**MySQL (aimee_db)**:
- **progress_snapshots**: 832件 ✅ **重要** - Q1~Q6実装の基盤
  - 受信時刻 (snapshot_time)
  - 納期 (expected_completion_time)
  - 残タスク数 (total_waiting)
  - 工程別件数 (entry_count, correction_waiting等)
- operators: 100件 (名前モック化済み)
- operator_process_capabilities: 191件
- login_records_by_location: 17件
- rag_context: 5件 (管理者ノウハウ)

**ChromaDB (aimee_knowledge)**:
- ポート: 8003 (Docker) / 8001 (ローカルpanasonicと共用)
- ドキュメント: 12件 (管理者ノウハウのみ)
- データソース: `/Users/umemiya/Desktop/erax/aimee-fe/管理者の判断材料・判断基準等について.txt`
- 埋め込みモデル: intfloat/multilingual-e5-small

**投入スクリプト**:
- `/Users/umemiya/Desktop/erax/aimee-db/extract_and_import_snapshots.py` - progress_snapshots投入
- `/Users/umemiya/Desktop/erax/aimee-db/import_manager_knowledge_to_chroma.py` - ChromaDB投入

### ハイブリッドRAG実装済み

**構成**: MySQL (構造化データ) + ChromaDB (管理者ノウハウ)

**実装箇所**:
- `ChromaService.search_manager_rules()`: 管理者ルール検索
- `IntegratedLLMService`: RAG統合ロジック
- `OllamaService`: プロンプトに管理者基準を含める
- `DatabaseService`: 6種類のintent_type対応

**対応するintent_type**:
1. `deadline_optimization`: 納期ベース最適化
2. `completion_time_prediction`: 完了時刻予測
3. `delay_risk_detection`: 遅延リスク検出
4. `impact_analysis`: 影響分析
5. `cross_business_transfer`: 業務間移動
6. `process_optimization`: 工程別最適化

### API精度テスト結果

**総合精度**: 100% 🎉 **全質問で100%達成！**

| 質問 | 精度 | 状態 | 実装内容 |
|------|------|------|----------|
| Q1: 納期20分前に完了 | 100% | ✅ | 4階層明示、業務間移動優先 |
| Q2: 移動元への影響 | 100% | ✅ | 会話履歴対応完了 |
| Q3: 業務間移動 | 100% | ✅ | 4階層明示、「人」キーワード |
| Q4: 完了時刻予測 | 100% | ✅ | progress_snapshots活用 |
| Q5: 工程別最適化 | 100% | ✅ | 4階層明示、工程別配置 |
| Q6: 遅延リスク検出 | 100% | ✅ | 遅延リスク検出ロジック |

**テストスクリプト**: `/Users/umemiya/Desktop/erax/aimee-fe/run_api_test.py`

**精度改善の軌跡**:
- 開始時: 0% (全問未実装)
- 第1回: 23.6%
- 第2回: 36.1%
- 第3回: 41.7%
- 第4回: 54.2%
- 第5回: 69.4%
- 第6回: 91.7%
- **最終: 100%** 🎉

### 実装完了した重要機能 (2025-10-20)

#### 1. 業務間移動優先ロジック実装 ✅
```
拠点間移動（札幌→品川）ではなく、
業務間移動（非SS→SS）を優先する仕組みを実装済み

例: 「非SS」の「新非SS」の「OCR対象」の「エントリ1」から2人を
    「SS」の「新SS(W)」の「OCR対象」の「エントリ1」へ移動
```

#### 2. 会話履歴管理実装 ✅
- メモリベースの会話履歴ストア（ConversationStore）
- セッションIDごとに会話履歴を管理
- Q2（影響分析）で直前の配置提案を参照可能

#### 3. 4階層明示対応 ✅
```
全ての配置提案で以下の4階層を明示：
1. 大分類 (SS / 非SS / あはき / 適用徴収)
2. 業務タイプ (新SS(W) / 新SS(片道) など)
3. OCR区分 (OCR対象 / OCR非対象 / 目検)
4. 工程名 (エントリ1 / エントリ2 / 補正 / SV補正)
```

---

## フロントエンド・バックエンド統合状況 (2025-10-08完了)

### ✅ 完了した統合作業

#### 1. APIエンドポイント統一
**問題**: ポート番号とエンドポイントの不一致
- バックエンド: `localhost:8000`、フロントエンド: `localhost:8002` を想定
- チャットAPI: `/api/v1/llm-test/integrated` と `/api/v1/chat/message` が混在

**解決策**:
- ✅ バックエンドを **8002番ポート** に統一
  - `aimee-be/.env`: `PORT=8002`
  - `aimee-be/start.py`: 起動ポート修正
- ✅ チャットAPIを `/api/v1/chat/message` に統一
  - `aimee-fe/frontend/src/utils/api_client.py:92` を修正

#### 2. 承認履歴DBテーブル追加
**要件**: 承認・却下された配置変更を履歴として保存し、別アプリが読み取れるようにする

**実装内容**:
- ✅ `approval_history` テーブル作成
  - 保存場所: `aimee-db/approval_history_table.sql`
  - DBに作成済み

**テーブル構造**:
```sql
CREATE TABLE approval_history (
    approval_history_id INT AUTO_INCREMENT PRIMARY KEY,
    suggestion_id VARCHAR(50) NOT NULL,           -- 提案ID
    suggestion_type VARCHAR(50),                  -- 提案タイプ
    changes JSON NOT NULL,                        -- 配置変更内容
    impact JSON,                                  -- 予測効果
    reason TEXT,                                  -- 提案理由
    confidence_score DECIMAL(5,4),                -- AI信頼度
    action_type ENUM('approved', 'rejected', 'modified'), -- アクション
    action_user VARCHAR(100),                     -- 承認者名
    action_user_id VARCHAR(50),                   -- 承認者ID
    feedback_reason TEXT,                         -- 承認/却下理由
    feedback_notes TEXT,                          -- 補足コメント
    execution_status ENUM('pending', 'executing', 'completed', 'failed'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

#### 3. 承認機能のAPI連携実装
**バックエンド側** (`aimee-be/app/api/v1/endpoints/approvals.py`):
- ✅ `save_approval_history()` 関数を追加
- ✅ 承認/却下時に自動的にDBに保存
- ✅ DB接続: `aimee-db/config.py` の `db_manager` を使用

**フロントエンド側** (`aimee-fe/frontend/app.py`):
- ✅ `get_pending_approvals()` をAPI連携に変更 (旧: モックデータ)
- ✅ 承認/却下ボタンで `api_client.execute_approval_action()` を呼び出し
- ✅ エラー時はモックデータで動作継続

#### 4. api_client.pyメソッド追加
**追加メソッド一覧**:
```python
# aimee-fe/frontend/src/utils/api_client.py

def get_pending_approvals(status, urgency) -> Dict:
    """承認待ち一覧を取得"""
    # GET /api/v1/approvals

def get_approval_detail(approval_id) -> Dict:
    """承認詳細を取得"""
    # GET /api/v1/approvals/{approval_id}

def execute_approval_action(approval_id, action, user, user_id, reason, notes) -> Dict:
    """承認/却下を実行"""
    # POST /api/v1/approvals/{approval_id}/action

def get_alert_detail(alert_id) -> Dict:
    """アラート詳細を取得"""
    # GET /api/v1/alerts/{alert_id}
```

---

## システム起動方法

### 🌐 AWS本番環境デプロイ（2025-10-24更新）⭐️

#### ワンコマンドデプロイ
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./deploy-to-aws.sh
```

**所要時間**: 約15分

**詳細**: [AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md) を参照

---

### 🚀 ローカル開発環境の起動方法（⭐推奨: Docker起動スクリプト）

#### 方法1: Docker起動スクリプト使用（推奨）

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 全体起動（バックエンド + フロントエンド）
./docker-start-all.sh

# または個別起動
./docker-start-backend.sh   # バックエンドのみ
./docker-start-frontend.sh  # フロントエンドのみ

# 状態確認
./docker-check-status.sh

# 停止
./docker-stop-all.sh

# ブラウザアクセス
open http://localhost:8501
```

**メリット**:
- ✅ 全依存サービスが自動的に起動
- ✅ 本番環境と同じ構成
- ✅ 環境構築が簡単

#### 方法2: Python直接実行（開発・デバッグ用）

コード修正を即座に反映したい場合:

```bash
# 1. 依存サービスのみDockerで起動
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose up -d ollama-main chromadb redis

# 2. バックエンド起動（ホットリロード有効）
cd /Users/umemiya/Desktop/erax/aimee-fe
./scripts/start_backend.sh

# 3. フロントエンド起動（別ターミナル）
./scripts/start_frontend.sh

# ブラウザアクセス
open http://localhost:8501
```

**メリット**:
- ✅ コード変更が即座に反映（--reload）
- ✅ デバッグが容易

#### データ投入確認

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as count FROM progress_snapshots')
print(f'progress_snapshots: {result[0][\"count\"]}件')
"
# 期待値: 832件

# データが不足している場合
./restore_dummy_data.sh
```

**詳細**: [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)

### DB接続確認
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "from config import db_manager; print(db_manager.test_connection())"
```

### 承認履歴確認
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT * FROM approval_history ORDER BY created_at DESC LIMIT 5')
for row in result:
    print(row)
"
```

---

## 使用フロー

### 1. チャットで配置提案を受け取る
1. フロントエンドのチャット画面で「札幌のエントリ1工程が遅延しています」と入力
2. バックエンドAI (`POST /api/v1/chat/message`) が配置変更を提案
3. 提案カードに「✅ 承認」「❌ 却下」「💬 詳細を相談」ボタンが表示

### 2. 承認/却下を実行
**承認の場合**:
1. ユーザーが「✅ 承認」ボタンをクリック
2. `api_client.execute_approval_action(approval_id, "approve", ...)` が呼ばれる
3. バックエンド: `POST /api/v1/approvals/{id}/action`
4. `save_approval_history()` がDBに保存
5. 別アプリが `approval_history` テーブルを `SELECT` して読み取り可能

**却下の場合**:
- 同様に `action="reject"` でDB保存

### 3. 承認待ち一覧で確認
1. 「✅ 配置承認」タブに切り替え
2. `GET /api/v1/approvals` で一覧取得
3. 各提案に対して一括承認/却下が可能

---

## API一覧

### チャット
- `POST /api/v1/chat/message` - AIチャット (配置提案生成)
- `GET /api/v1/chat/history` - チャット履歴取得

### 承認
- `GET /api/v1/approvals` - 承認待ち一覧取得
- `GET /api/v1/approvals/{id}` - 承認詳細取得
- `POST /api/v1/approvals/{id}/action` - 承認/却下実行

### アラート
- `GET /api/v1/alerts` - アラート一覧取得
- `GET /api/v1/alerts/{id}` - アラート詳細取得
- `GET /api/v1/alerts/check` - アラート基準チェック
- `POST /api/v1/alerts/{id}/resolve` - アラート解消提案

---

## データベース情報

### ローカル環境
- **DB名**: `aimee_db`
- **ユーザー**: `aimee_user`
- **パスワード**: `Aimee2024!`
- **ホスト**: `localhost:3306`
- **データ**: モック名（100名）

### AWS本番環境（RDS）
- **DB名**: `aimee_db`
- **ユーザー**: `admin`
- **パスワード**: `Aimee2024!RDS`
- **エンドポイント**: `aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306`
- **データ**: モック名（100名） ※実名データは未投入

### 主要テーブル
- `locations`: 拠点マスタ
- `businesses`: 業務マスタ
- `processes`: 工程マスタ
- `operators`: オペレータマスタ
- `operator_work_records`: オペレータ作業実績
- `progress_snapshots`: 進捗スナップショット
- `login_records`: ログイン記録
- **`approval_history`**: 承認履歴 (新規追加) ← 別アプリがこれを読む

---

## 設定ファイル

### バックエンド環境変数 (.env)
```env
# aimee-be/.env
APP_NAME=AIMEE-Backend
APP_VERSION=1.0.0
DEBUG=true
ENVIRONMENT=development

# API設定
HOST=0.0.0.0
PORT=8002
API_V1_PREFIX=/api/v1

# データベース設定
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@localhost:3306/aimee_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# CORS設定
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

### フロントエンド環境変数
```python
# aimee-fe/frontend/src/utils/api_client.py:17
self.base_url = base_url or os.getenv("AIMEE_API_URL", "http://localhost:8002")
```

---

## 現在の実装状況

### ✅ 完全実装済み（コア機能）
- ✅ APIエンドポイント統一 (8002ポート)
- ✅ **承認・否認機能のDB保存** (approval_history完全対応)
- ✅ 承認/却下のフロント・バック連携
- ✅ api_client.pyメソッド拡張
- ✅ **ハイブリッドRAG実装** (MySQL + ChromaDB)
- ✅ **6種類のintent_type対応** (Q1~Q6)
- ✅ **スキルベースマッチング** (異なる工程間移動)
- ✅ **業務間移動優先ロジック** (拠点→業務)
- ✅ **会話履歴管理** (ConversationStore)
- ✅ **4階層明示対応** (全配置提案)
- ✅ **100%精度達成** (全質問対応)

### ⚠️ モックデータで動作中
- アラート生成 (`check_alerts`) - 今後実データ対応予定

### 🔧 今後の拡張ポイント
1. **認証機能**: ユーザーログイン実装
2. **WebSocket通知**: リアルタイム通知
3. **自動更新**: 2分間隔でデータポーリング (要件書より)
4. **実配置データ取得**: RealWorksとの連携
5. **リアルタイム配置データAPI**: 現在の配置状況取得
6. **アラート実データ対応**: progress_snapshotsベースのアラート生成

---

## トラブルシューティング

### バックエンドが起動しない
```bash
# DB接続確認
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "from config import db_manager; print(db_manager.test_connection())"

# ポート確認
lsof -i:8002
```

### フロントエンドでAPI接続エラー
- バックエンドが起動しているか確認: `http://localhost:8002/docs` にアクセス
- フロントエンドはAPI接続失敗時にモックデータで動作継続

### DB接続エラー
```bash
# MySQL起動確認
mysql.server status

# 権限確認
mysql -u aimee_user -p'Aimee2024!' aimee_db -e "SHOW TABLES;"
```

---

## 未解決の質問・要確認事項

### 高優先度
1. **リアルタイム配置データ取得API**: 現在の配置状況を取得するエンドポイントは必要か?
2. **WebSocket vs ポーリング**: 通知機能はどちらで実装するか?
3. **バックエンドのAPIスキーマ**: ChatResponseに`suggestion`が含まれているか確認

### 中優先度
4. **RAG検索結果の表示**: `recommended_operators`をUIでどう表示するか?
5. **アラートルールソース**: Alertスキーマに`rule_source`フィールドは存在するか?
6. **エラーハンドリング**: 本番環境ではエラーメッセージを表示? それともモックデータで継続?
7. **フィードバック送信API**: 承認/却下理由をRAGに取り込むための専用エンドポイントは必要か?

### 低優先度
8. **認証機能**: ユーザー認証は必要か?
9. **環境変数管理**: 開発/本番環境の切り替え方法は?
10. **データ更新頻度**: フロントエンドで自動更新(polling)を実装するか?

---

## 参考資料

- **要件定義書**: `aimee-fe/01_requirements/requirements.md`
- **DB設計書**: `aimee-fe/02_database/design/02_table_specifications.md`
- **統合ガイド**: `aimee-fe/INTEGRATION.md`
- **システム構成図**: [diagrams.net](https://app.diagrams.net/?splash=0#G1kBIJvslm_yRlK2QyCbrDwr9GZnJFTb3X)
- **全体概要**: [Notion](https://pouncing-attic-dd0.notion.site/24154d8b9bc0807c8dfbc7278e5655cf)

---

## Docker構成

### バックエンド (aimee-be)
- **Compose**: `docker-compose.yml` (本番用), `docker-compose-mac-m3.yml` (Mac M3用)
- **サービス**:
  - `api`: FastAPIアプリケーション (ポート8002)
  - `mysql`: MySQL 8.0 (ポート3306)
  - `redis`: Redis 7 (ポート6380)
  - `chromadb`: ベクトルDB (ポート8002 - APIと共有)
  - `ollama-light`: 意図解析LLM (gemma2:2b) (ポート11435)
  - `ollama-main`: 応答生成LLM (gemma3:4b) (ポート11435)

### フロントエンド (aimee-fe)
- **Dockerfile**: `Dockerfile`
- **Compose**: `docker-compose.yml`
- **サービス**:
  - `frontend`: Streamlitアプリケーション (ポート8501)
- **接続**: `host.docker.internal:8002` でバックエンドAPIに接続

### ポート一覧
- **8002**: バックエンドAPI + ChromaDB (ポート競合注意)
- **8501**: フロントエンド (Streamlit)
- **3306**: MySQL
- **6380**: Redis
- **11433**: Ollama Light (軽量LLM)
- **11435**: Ollama Main (メインLLM)

---

## 更新履歴

- **2025-10-26 (v3)**: ファイル整理・モデル復元 🎉
  - ファイル整理実施（26件削除、198KB削減）
  - 00_INDEX.md作成（プロジェクト完全索引）
  - プロジェクトルール追加（ドキュメント管理、DB管理）
  - **MAIN_MODEL復元**: gemma2:2b → gemma3:4b
  - モデル変更理由の特定と修正
  - デグレ防止テスト実施（API精度95.8%）

- **2025-10-26 (v2)**: 承認・否認機能のDB保存対応完了 🎉
  - approval_history への完全対応
  - Pydantic v2対応（model_dump）
  - 承認・否認ボタンのDB登録成功
  - RAG学習準備完了（承認/否認履歴の蓄積）
  - テスト実施（承認2件、否認2件確認）
  - マスタードキュメント更新（QUICK_REFERENCE.md作成）

- **2025-10-24 (v2)**: スキルベースマッチング実装完了 🎉🎉
  - **異なる工程間移動を実現**（エントリ2 → エントリ1）
  - スキルベースマッチングアルゴリズム実装
  - 拠点情報を完全削除（4階層のみ）
  - Pydanticスキーマ更新（AllocationChange）
  - 全質問100%維持（新ロジックで再テスト成功）
  - SYSTEM_OVERVIEW.md大幅更新
  - deploy-to-aws.sh作成（ワンコマンドデプロイ）
  - ドキュメント整理（documentsフォルダ）
  - DATABASE_STATUS.md作成

- **2025-10-24 (v1)**: CLAUDE.md最新版更新
  - 最新の実装状況を反映（100%達成）
  - 本番環境URLを追加
  - ドキュメント一覧を整理

- **2025-10-20**: API精度100%達成 🎉
  - 業務間移動優先ロジック実装完了
  - 会話履歴管理実装完了（ConversationStore）
  - 4階層明示対応完了
  - Q1~Q6全問100%達成

- **2025-10-17**: ハイブリッドRAG実装完了
  - progress_snapshots 832件投入
  - ChromaDB管理者ノウハウ12件投入
  - 6種類のintent_type実装
  - API精度54.2%達成

- **2025-10-08**: フロントエンド・バックエンド統合完了
  - ポート8002統一
  - 承認履歴DB実装
  - API連携完了
  - CLAUDE.md作成
  - Docker起動スクリプト作成
  - フロントエンドDocker化完了

---

## 📂 データ再投入方法 (次回起動時)

### progress_snapshotsが空の場合

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 extract_and_import_snapshots.py
```

### ChromaDBが空の場合 (aimee_knowledgeコレクション)

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# aimee-be用ChromaDB (ポート8003) に投入
python3 << 'PYEOF'
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.HttpClient(host='localhost', port=8003)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-small"
)

collection = client.get_or_create_collection(
    name="aimee_knowledge",
    embedding_function=embedding_function
)

# 管理者ノウハウを読み込み
with open('/Users/umemiya/Desktop/erax/aimee-fe/管理者の判断材料・判断基準等について.txt', 'r') as f:
    content = f.read()

# チャンキングして投入
sections = [s.strip() for s in content.split('\n\n') if s.strip() and len(s.strip()) > 10]
collection.add(
    documents=sections,
    ids=[f"rule_{i}" for i in range(len(sections))],
    metadatas=[{"category": "manager_rule", "source": "管理者の判断材料.txt"} for _ in sections]
)

print(f"✅ {len(sections)}件投入完了")
PYEOF
```

---

## 📚 重要なドキュメント

### 🔥 最重要
- **[00_INDEX.md](./00_INDEX.md)** ⭐️⭐️⭐️⭐️⭐️ - **プロジェクト完全索引**
  - 全ドキュメント・スクリプトへのリンク
  - 用途別検索ガイド
  - クイックコマンド集

- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** ⭐️⭐️⭐️⭐️ - **全ての最新情報を1ページで**
  - DB環境（ローカル/AWS RDS）
  - AI/LLMモデル（qwen2、gemma2、ChromaDB）
  - デプロイ方法（ワンコマンド）
  - 起動方法、API情報、セキュリティ
  - トラブルシューティング

### 📊 システム全体像
- **[SYSTEM_OVERVIEW.md](./SYSTEM_OVERVIEW.md)** - 一目でわかるシステム全体図（Mermaid）⭐️⭐️⭐️
  - 処理フロー図（5ステップ）
  - ハイブリッドRAGの仕組み
  - 提案生成ロジックの詳細
  - 処理時間の内訳

- **[SYSTEM_ARCHITECTURE.md](./documents/SYSTEM_ARCHITECTURE.md)** - システムアーキテクチャ詳解
  - 技術スタック詳細
  - 各技術の選定理由
  - データフローの詳細

### 作業ログ・レポート

- **[IMPLEMENTATION_LOG.md](./IMPLEMENTATION_LOG.md)** - 全作業ログ (2025-10-20完了) ⭐️
  - データ投入手順
  - ハイブリッドRAG実装過程
  - APIテスト結果 (7回分)
  - 精度改善の履歴（0% → 100%）
  - 業務間移動優先の実装詳細
  - 会話履歴対応の実装詳細

- **[DATABASE_STATUS.md](../aimee-db/DATABASE_STATUS.md)** ⭐️ - データベース状況（2025-10-24最新版）
  - 本番データ vs モックデータの区別
  - 全20テーブルの詳細情報
  - データソース一覧
  - セキュリティポリシー
  - ChromaDBの状況

- **[reports/](./documents/reports/)** - バグ報告と新要件分析
  - バグ報告 (4件) - 2件修正済み
  - 新要件分析 (Q1~Q6) - 全問100%達成
  - 実装可能性レポート

### テスト関連

- **[run_api_test.py](./run_api_test.py)** - APIテストスクリプト（Q1~Q6）
- **[api_test_results.json](./api_test_results.json)** - 最新テスト結果（100%達成）
- **[documents/test_q1_q2_conversation.py](./documents/test_q1_q2_conversation.py)** - 会話履歴テスト
- **[documents/test_cases_q1_q6.json](./documents/test_cases_q1_q6.json)** - テストケース定義
- **[documents/api_test_*.log](./documents/)** - 過去のテストログ

### セットアップ・デプロイ

- **[INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md)** - ローカル開発環境のセットアップ
- **[DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)** ⭐️ - AWS本番環境デプロイ手順（ワンコマンド）
- **[deploy-to-aws.sh](./deploy-to-aws.sh)** - 自動デプロイスクリプト
- **[documents/AWS_DEPLOY_GUIDE.md](./documents/AWS_DEPLOY_GUIDE.md)** - AWS詳細デプロイ手順

### デモ

- **[DEMO_SCRIPT_FINAL.md](./DEMO_SCRIPT_FINAL.md)** - デモ実施手順
- **[documents/REAL_DATA_SUCCESS.md](./documents/REAL_DATA_SUCCESS.md)** - 実データでのテスト結果
- **[documents/DEMO_VIDEO_SCRIPT.md](./documents/DEMO_VIDEO_SCRIPT.md)** - デモ動画用台本
- **[documents/DEMO_QUESTIONS.md](./documents/DEMO_QUESTIONS.md)** - デモ用質問パターン

---

## ⚠️ 既知の問題

### バグ (documents/reports/bug_reports/BUG_REPORT.md)

**修正済み (2025-10-24/10-26)**:
- ~~配置提案ロジックが不適切~~ → ✅ スキルベースマッチング実装済み
- ~~会話履歴未対応~~ → ✅ ConversationStore実装済み
- ~~Q3/Q5ロジック未実装~~ → ✅ 全問100%達成
- ~~承認/否認ボタンのDB保存~~ → ✅ approval_history完全対応（2025-10-26）

**残課題**:
1. 複数人提案の表示改善 (優先度: 低) - フロントエンドUI改善

### API精度

**全質問100%達成** ✅
- Q1 (納期最適化): 100% ✅
- Q2 (影響分析): 100% ✅
- Q3 (業務間移動): 100% ✅
- Q4 (完了時刻予測): 100% ✅
- Q5 (工程別最適化): 100% ✅
- Q6 (遅延リスク検出): 100% ✅

---

## 🔧 トラブルシューティング

### ChromaDBに接続できない

```bash
# Dockerコンテナを確認
docker ps | grep chroma

# aimee-be用ChromaDB (ポート8003) が起動しているか確認
curl http://localhost:8003/api/v1/heartbeat

# 起動していない場合
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose up -d chromadb
```

### Ollamaが応答しない

```bash
# Ollamaコンテナを確認
docker ps | grep ollama

# モデルリストを確認
docker exec aimee-be-ollama-main-1 ollama list

# モデルが未ダウンロードの場合
docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b
```

### progress_snapshotsが空

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 extract_and_import_snapshots.py
```

### APIが「現在のリソースで対応可能です」しか返さない

1. progress_snapshotsが投入されているか確認
2. Ollamaが起動しているか確認
3. ChromaDBにaimee_knowledgeコレクションがあるか確認

---

