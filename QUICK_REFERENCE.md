# AIMEE クイックリファレンス

**最終更新**: 2025-10-24
**バージョン**: 2.0.0 - スキルベースマッチング実装

すべての重要情報をこの1ページで確認できます。

---

## 📑 目次

1. [システム概要](#システム概要)
2. [アクセスURL](#アクセスurl)
3. [データベース環境](#データベース環境)
4. [AI/LLMモデル](#aillmモデル)
5. [デプロイ方法](#デプロイ方法)
6. [起動方法](#起動方法)
7. [API情報](#api情報)
8. [データ状況](#データ状況)
9. [セキュリティ](#セキュリティ)
10. [トラブルシューティング](#トラブルシューティング)

---

## 🎯 システム概要

### プロジェクト名
**AIMEE** (AI配置最適化システム)

### 目的
トランスコスモス様の健保組合業務における人員配置を、AI技術で自動化・効率化

### 主な機能
- ✅ **スキルベースマッチング**: 異なる工程間移動（エントリ2 → エントリ1）
- ✅ **4階層のみ表記**: 拠点名なし、業務階層のみ
- ✅ **ハイブリッドRAG**: MySQL（定量）+ ChromaDB（定性）
- ✅ **会話履歴管理**: ConversationStore実装
- ✅ **承認・否認機能**: DB保存完全対応、RAG学習準備完了
- ✅ **API精度100%**: 全6問で100%達成

### 技術スタック
- **フロントエンド**: Streamlit (Python)
- **バックエンド**: FastAPI (Python, 非同期)
- **AI/LLM**: Ollama (qwen2:0.5b, gemma2:2b)
- **データベース**: MySQL, ChromaDB, Redis
- **インフラ**: AWS EC2, RDS

---

## 🌐 アクセスURL

### ローカル開発環境
- **フロントエンド**: http://localhost:8501
- **バックエンドAPI**: http://localhost:8002
- **API Docs**: http://localhost:8002/docs
- **MySQL**: localhost:3306

### AWS本番環境
- **フロントエンド**: http://43.207.175.35:8501
- **バックエンドAPI**: http://54.150.242.233:8002
- **API Docs**: http://54.150.242.233:8002/docs
- **RDS MySQL**: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306

---

## 💾 データベース環境

### バックアップ・復元・切り替え

#### データ切り替え（ワンコマンド）⭐️

**実名データに切り替え**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_real_data.sh
```

**ダミーデータに切り替え**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_dummy_data.sh
```

**注**: スクリプトは実行前に自動バックアップを作成します

---

#### 利用可能なバックアップ

| ファイル名 | データ種類 | 用途 |
|-----------|----------|------|
| `backups/aimee_db_production_20251029_203725.sql` | **実名データ** (2,832人) | 本番・内部分析 |
| `backups/aimee_db_production_dummy.sql` | **ダミーデータ** (2,832人) | 共有・デモ |

---

#### 手動バックアップ作成

```bash
cd /Users/umemiya/Desktop/erax/aimee-db
export MYSQL_PWD='Aimee2024!'
mysqldump -u aimee_user aimee_db > backups/aimee_db_backup_$(date +%Y%m%d_%H%M%S).sql
unset MYSQL_PWD
```

---

### ローカル環境

**MySQL**:
- **ホスト**: localhost:3306
- **ユーザー**: aimee_user
- **パスワード**: Aimee2024!
- **DB名**: aimee_db
- **データ**: 実名データ2,832人（2025-10-29投入）

**ChromaDB**:
- **ホスト**: localhost:8003
- **コレクション**: aimee_knowledge
- **ドキュメント**: 12件（管理者ノウハウ）

**Redis**:
- **ホスト**: localhost:6380
- **用途**: 会話履歴キャッシュ

### AWS本番環境

**RDS MySQL**:
- **エンドポイント**: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306
- **ユーザー**: admin
- **パスワード**: Aimee2024!RDS
- **DB名**: aimee_db
- **データ**: モック名（100名）
- **インスタンス**: db.t3.micro
- **ストレージ**: 20GB

**ChromaDB**:
- **ホスト**: EC2内 localhost:8003（Dockerコンテナ）
- **コレクション**: aimee_knowledge
- **ドキュメント**: 12件

**Redis**:
- **ホスト**: EC2内 localhost:6380（Dockerコンテナ）
- **用途**: 会話履歴、セッション管理

### データ件数（2025-10-24時点）

| テーブル名 | 件数 | データ種類 |
|-----------|------|----------|
| operators | 100 | モック名 |
| operator_process_capabilities | 191 | 実データ |
| progress_snapshots | 832 | 実データ |
| locations | 7 | 実データ |
| businesses | 12 | 実データ |
| processes | 46 | 実データ |
| rag_context | 5 | 実データ |
| manager_rules | 5 | 実データ |
| **approval_history** | **4** | **運用データ** |
| workload_forecasts | 6 | 実データ |
| **合計** | **1,208** | - |

---

## 🤖 AI/LLMモデル

### 使用モデル一覧

#### 1. qwen2:0.5b（軽量モデル）
- **用途**: 意図解析、メッセージ分類
- **パラメータ数**: 5億
- **メモリ使用量**: 約1GB
- **応答速度**: 0.5秒
- **ポート**: 11433（Dockerコンテナ）

**実行環境**: Ollama Light
```bash
# モデル確認
docker exec aimee-be-ollama-light-1 ollama list
```

---

#### 2. gemma3:4b（メインモデル）⭐️
- **用途**: 応答生成、自然言語説明
- **パラメータ数**: 40億
- **メモリ使用量**: 約8GB
- **応答速度**: 3-4秒
- **ポート**: 11435（Dockerコンテナ）

**実行環境**: Ollama Main
```bash
# モデル確認
docker exec aimee-be-ollama-main-1 ollama list
```

**注**: `.env`では`MAIN_MODEL=gemma3:4b`と設定（2025-10-26に復元）

---

#### 3. gemma2:2b（予備モデル）
- **用途**: 軽量な応答生成（メモリ不足時の代替）
- **パラメータ数**: 20億
- **メモリ使用量**: 約2GB
- **応答速度**: 2-3秒

**注**: gemma3:4bがメモリ不足で動作しない場合の代替モデル（ダウンロード済み）

---

#### 4. intfloat/multilingual-e5-small（埋め込みモデル）
- **用途**: ChromaDBのベクトル化
- **次元数**: 384次元
- **言語**: 多言語対応（日本語に強い）
- **実行環境**: ChromaDBコンテナ内

---

### モデル選定の理由

| モデル | 選定理由 |
|--------|---------|
| **qwen2:0.5b** | 高速な意図解析、メモリ効率 |
| **gemma2:2b** | 品質とスピードのバランス |
| **Ollama** | ローカル実行、データ外部流出なし、コスト削減 |
| **multilingual-e5-small** | 日本語に強い、軽量 |

---

## 🚀 デプロイ方法

### AWS本番環境デプロイ（ワンコマンド）⭐️

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./deploy-to-aws.sh
```

**所要時間**: 約15分

**実行内容**:
1. SSH接続確認
2. フロントエンドビルド・デプロイ（約5分）
3. バックエンドビルド・デプロイ（約10分）
4. 動作確認テスト

**個別デプロイ**:
```bash
./deploy-to-aws.sh frontend  # フロントエンドのみ
./deploy-to-aws.sh backend   # バックエンドのみ
```

**詳細**: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)

---

### 手動デプロイ

#### フロントエンド
```bash
# アーカイブ作成
tar --exclude='.git' --exclude='*.pyc' -czf /tmp/aimee-fe.tar.gz .

# EC2転送
scp -i ~/.ssh/aimee-key.pem /tmp/aimee-fe.tar.gz ubuntu@43.207.175.35:~/

# デプロイ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down && \
     tar -xzf ~/aimee-fe.tar.gz && \
     docker-compose up -d --build"
```

#### バックエンド
```bash
# アーカイブ作成
cd /Users/umemiya/Desktop/erax/aimee-be
tar --exclude='.git' --exclude='chroma-data' -czf /tmp/aimee-be.tar.gz app .env docker-compose.yml

# EC2転送
scp -i ~/.ssh/aimee-key.pem /tmp/aimee-be.tar.gz ubuntu@54.150.242.233:~/

# デプロイ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down && \
     tar -xzf ~/aimee-be.tar.gz && \
     docker-compose up -d"
```

---

## 🔧 起動方法

### ローカル環境

#### 推奨起動方法（Docker）

**ステップ1**: Dockerサービス起動
```bash
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose up -d ollama-light ollama-main chromadb redis
```

**ステップ2**: バックエンド起動（ローカル）
```bash
cd /Users/umemiya/Desktop/erax/aimee-be
python3 start.py
# または
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

**ステップ3**: フロントエンド起動
```bash
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
streamlit run app.py
```

**アクセス**: http://localhost:8501

---

#### 簡易起動（Dockerスクリプト）

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# 全体起動
./docker-start-all.sh

# 状態確認
./docker-check-status.sh

# 停止
./docker-stop-all.sh
```

---

### AWS本番環境

#### 起動状態確認

```bash
# フロントエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "docker ps | grep aimee-frontend"

# バックエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker ps | grep aimee-be"
```

#### 再起動

```bash
# フロントエンド再起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose restart"

# バックエンド再起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose restart"
```

#### 全サービス再起動

```bash
# バックエンド停止→起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down && docker-compose up -d"

# フロントエンド停止→起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down && docker-compose up -d"
```

---

## 📡 API情報

### エンドポイント一覧

#### チャット
- `POST /api/v1/chat/message` - AIチャット（配置提案生成）
- `GET /api/v1/chat/history` - チャット履歴取得

**リクエスト例**:
```json
{
  "message": "SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。",
  "context": {},
  "session_id": "user_12345"
}
```

**レスポンス例**:
```json
{
  "response": "エントリ2からエントリ1への移動により3名の追加配置を提案します...",
  "suggestion": {
    "id": "SGT20251024-XXXXXX",
    "changes": [
      {
        "from_business_category": "SS",
        "from_business_name": "新SS(W)",
        "from_process_category": "OCR非対象",
        "from_process_name": "エントリ2",
        "to_business_category": "SS",
        "to_business_name": "新SS(W)",
        "to_process_category": "OCR非対象",
        "to_process_name": "エントリ1",
        "count": 1,
        "operators": ["稲實　百合子"],
        "is_cross_business": false
      }
    ],
    "impact": {
      "productivity": "+30%",
      "delay": "-45分",
      "quality": "維持"
    }
  }
}
```

---

#### 承認・否認（DB保存対応済み）✅
- `GET /api/v1/approvals` - 承認待ち一覧取得
- `GET /api/v1/approvals/{id}` - 承認詳細取得
- `POST /api/v1/approvals/{id}/action` - 承認/却下実行（DB保存）

**リクエスト例（承認）**:
```json
{
  "action": "approve",
  "user": "管理者テスト",
  "user_id": "test_admin",
  "reason": "納期対応のため承認",
  "notes": "スキルベースマッチングによる提案を承認"
}
```

**リクエスト例（否認）**:
```json
{
  "action": "reject",
  "user": "管理者テスト",
  "user_id": "test_admin",
  "reason": "移動元の人員が不足しているため却下",
  "notes": "代替案を検討してください"
}
```

**DB保存内容（approval_history）**:
- 提案ID、配置変更内容（JSON、4階層構造）
- 承認/却下アクション、実行者、実行日時
- 承認/却下理由、補足コメント
- 将来のRAG学習に活用可能

#### アラート
- `GET /api/v1/alerts` - アラート一覧取得
- `GET /api/v1/alerts/{id}` - アラート詳細取得
- `POST /api/v1/alerts/{id}/resolve` - アラート解消提案

#### ヘルスチェック
- `GET /api/v1/health` - システム状態確認

```bash
# ローカル
curl http://localhost:8002/api/v1/health

# AWS
curl http://54.150.242.233:8002/api/v1/health
```

---

## 📊 データ状況

### 現在投入されているデータ

| テーブル名 | 件数 | データ種類 | 備考 |
|-----------|------|----------|------|
| **operators** | 100 | モック名 | 竹下　朱美、高山　麻由子等 |
| **operator_process_capabilities** | 191 | 実データ | スキル情報 |
| **progress_snapshots** | 832 | 実データ | 2025年7月の実業務進捗 |
| **locations** | 7 | 実データ | 札幌、品川、本町東、西梅田、沖縄、佐世保、和歌山 |
| **businesses** | 12 | 実データ | SS、非SS、あはき、適用徴収 |
| **processes** | 46 | 実データ | エントリ1、エントリ2、補正、SV補正、目検 |
| **rag_context** | 5 | 実データ | RAGコンテキスト |
| **manager_rules** | 5 | 実データ | 管理者ルール |
| **approval_history** | 4 | 運用データ | 承認/否認履歴（RAG学習用） |
| **workload_forecasts** | 6 | 実データ | 負荷予測 |

**合計**: 1,208件

**approval_history の内訳**:
- 承認（approved）: 2件
- 否認（rejected）: 2件
- 4階層構造の配置変更内容（JSON）
- 承認/否認理由、実行者、実行日時を記録
- 将来のRAG精度向上に活用予定

### データの種類

#### 本番データ（実名）⚠️ 機密情報
- **ファイル**: `01_real_data_only.sql`（11KB）
- **内容**: スキーマ定義のみ
- **実データ**: 含まれない（別途「資料」フォルダからPythonスクリプトでインポートする想定）
- **⚠️ 注意**: 実名2,664名の元データ（Excel/CSV）は現在存在しない

#### 擬似データ（モック名）✅ 開発・デモ用（現在使用中）
- **ファイル**: `real_data_with_mock_names.sql`（3.9MB）
- **オペレータ**: 100名（**日本人風の仮名**）
- **スキル情報**: 191件（全てINSERT文として含まれる）
- **モック名例**: 竹下　朱美、高山　麻由子、上野　由香利、稲實　百合子、萩野　裕子
- **用途**: 開発、テスト、デモ
- **特徴**: このファイル1つで完全なデータセットを投入可能

#### 進捗データ（実データ）
- **ファイル**: `progress_snapshots_insert.sql`（73KB）
- **件数**: 832件
- **内容**: 2025年7月の実業務進捗（受信時刻、納期、残タスク数）

### データソース

| データ | 元ソース | 抽出方法 |
|--------|---------|---------|
| progress_snapshots | RealWorksManager KENPO_FSファイル | `extract_and_import_snapshots.py` |
| operators | 実オペレータ情報 → モック化 | `real_data_with_mock_names.sql` |
| 管理者ノウハウ | `管理者の判断材料・判断基準等について.txt` | `import_manager_knowledge_to_chroma.py` |

---

## 🔐 セキュリティ

### データ保護対策

#### 1. 人物名のモック化
- ✅ 開発・デモ環境では実名を使用しない
- ✅ 100名の日本人風仮名を使用
- ✅ それ以外のデータ（拠点、業務、進捗）は実データ

#### 2. パスワードの保護
- ✅ 全パスワードはハッシュ化（bcrypt）
- ✅ 平文パスワードはDB未格納

#### 3. データファイルの管理
- ✅ `.gitignore`に本番データファイルを追加
  - `01_real_data_only.sql`
  - `real_data_complete.sql`
  - `*_real_data_*.sql`
- ✅ Gitにコミットされないよう保護

#### 4. アクセス制限
- ✅ RDSはEC2からのみアクセス可能
- ✅ セキュリティグループで制限
- ✅ SSHキー認証（パスワード認証無効）

### 機密情報の取り扱いルール

| ファイル | 取扱区分 | 許可される操作 |
|---------|---------|--------------|
| `01_real_data_only.sql` | ⚠️ 機密 | 閲覧・実行のみ、共有・公開禁止 |
| `real_data_complete.sql` | ⚠️ 機密 | 閲覧・実行のみ、共有・公開禁止 |
| `real_data_with_mock_names.sql` | ✅ 安全 | 開発・テスト・デモ使用OK |
| `progress_snapshots_insert.sql` | △ 業務データ | 慎重に取り扱う |

---

## 🎯 スキルベースマッチングの仕組み

### アルゴリズム概要

#### 従来の問題
```
❌ エントリ1 → エントリ1（同じ工程間の移動、意味がない）
❌ 拠点間移動の表記（札幌 → 品川）
```

#### 新しい実装（2025-10-24）
```
✅ エントリ2 → エントリ1（異なる工程間の移動）
✅ 4階層のみの表記（拠点名なし）
✅ スキル保有を確認済み（品質保証）
```

### 処理フロー

1. **不足工程を特定**
   - 例: SSの「エントリ1」が1名不足

2. **スキル保有者を全検索**
   ```sql
   SELECT operator_name, current_process, target_process
   FROM operator_process_capabilities
   WHERE target_process = 'エントリ1'  -- エントリ1ができる人
     AND work_level >= 1
   ```
   - 結果: 99名がエントリ1のスキル保有

3. **現在の配置工程を確認**
   - 稲實　百合子さん: エントリ1スキル保有、現在「エントリ2」に配置
   - 萩野　裕子さん: エントリ1スキル保有、現在「エントリ2」に配置

4. **異なる工程からの移動候補を抽出**
   ```python
   if operator.current_process != shortage_process:
       # エントリ2 → エントリ1 の移動候補
   ```

5. **業務間移動を優先してソート**
   - 1位: 非SS のエントリ2 → SS のエントリ1（業務間）
   - 2位: あはき のエントリ2 → SS のエントリ1（業務間）
   - 3位: SS のエントリ2 → SS のエントリ1（同一業務）

6. **配置変更案を生成（4階層のみ）**
   ```
   「SS」の「新SS(W)」の「OCR非対象」の「エントリ2」から
   稲實　百合子さんを「OCR非対象」の「エントリ1」へ1人移動
   ```

---

## 📝 設定ファイル

### バックエンド環境変数（.env）

**ローカル環境**:
```env
# API設定
PORT=8002
HOST=0.0.0.0

# データベース
DATABASE_URL=mysql+aiomysql://aimee_user:Aimee2024!@localhost:3306/aimee_db

# Ollama
OLLAMA_LIGHT_HOST=localhost
OLLAMA_LIGHT_PORT=11433
OLLAMA_MAIN_HOST=localhost
OLLAMA_MAIN_PORT=11435
LIGHT_MODEL=qwen2:0.5b
MAIN_MODEL=gemma2:2b

# ChromaDB
CHROMADB_HOST=localhost
CHROMADB_PORT=8003

# Redis
REDIS_URL=redis://localhost:6380/0
```

**AWS環境**:
```env
DATABASE_URL=mysql+aiomysql://admin:Aimee2024!RDS@aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306/aimee_db

# その他はローカルと同じ（Dockerコンテナ内）
```

---

### フロントエンド環境変数

**ローカル環境**:
```python
# frontend/src/utils/api_client.py
AIMEE_API_URL = "http://localhost:8002"
```

**AWS環境**:
```yaml
# docker-compose.yml
environment:
  - AIMEE_API_URL=http://54.150.242.233:8002
```

---

## 🎬 デモ実施方法

### 推奨質問文

**Q1: 納期対応の配置提案**
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```

**期待される応答**:
- ✅ 異なる工程間移動（エントリ2 → エントリ1）
- ✅ 4階層明示
- ✅ 実名表示
- ✅ 3件の配置変更提案

**Q2: 影響分析**
```
配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?
```

**期待される応答**:
- ✅ Q1の提案を参照
- ✅ 4階層で影響分析
- ✅ 移動元の確認事項を提示

---

## 🛠️ トラブルシューティング

### よくある問題と解決方法

#### 1. APIが「現在のリソースで対応可能です」しか返さない

**原因**: データが投入されていない

**解決方法**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# 1. progress_snapshots確認
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as c FROM progress_snapshots;')
print(f'progress_snapshots: {result[0][\"c\"]}件')
"
# 期待値: 832件

# 2. 0件の場合、投入
python3 extract_and_import_snapshots.py
```

---

#### 2. Ollamaが応答しない

**原因**: モデルが未ダウンロード

**解決方法**:
```bash
# ローカル
docker exec aimee-be-ollama-light-1 ollama pull qwen2:0.5b
docker exec aimee-be-ollama-main-1 ollama pull gemma2:2b

# AWS
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker exec aimee-be-ollama-main-1 ollama list"
```

---

#### 3. ChromaDBに接続できない

**原因**: Dockerコンテナが起動していない

**解決方法**:
```bash
# ローカル
docker ps | grep chroma
docker-compose up -d chromadb

# ヘルスチェック
curl http://localhost:8003/api/v1/heartbeat
```

---

#### 4. フロントエンドからバックエンドに接続できない

**原因**: AIMEE_API_URLの設定ミス

**確認方法**:
```bash
# ローカル
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
python3 -c "import os; print(os.getenv('AIMEE_API_URL', 'http://localhost:8002'))"

# AWS
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker exec aimee-frontend env | grep AIMEE_API_URL"
# 期待値: AIMEE_API_URL=http://54.150.242.233:8002
```

---

#### 5. Docker Composeのプラットフォームエラー

**症状**: `exec format error` または `platform mismatch`

**原因**: Mac（arm64）とAWS（amd64）のプラットフォーム不一致

**解決方法**:
```bash
# docker-compose.ymlを確認
grep "platform:" docker-compose.yml

# ローカル（Mac M3）: platform: linux/arm64/v8
# AWS: platform: linux/amd64
```

---

## 📚 重要ドキュメント

### 必読ドキュメント
1. **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** ⭐️⭐️⭐️
   - システム全体図（Mermaid）
   - 処理フロー（5ステップ）
   - スキルベースマッチングの仕組み

2. **[CLAUDE.md](CLAUDE.md)** ⭐️⭐️
   - プロジェクト詳細
   - API一覧
   - 起動方法

3. **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** ⭐️
   - ローカル環境セットアップ手順

4. **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** ⭐️
   - AWS本番環境デプロイ手順

5. **[DATABASE_STATUS.md](../aimee-db/DATABASE_STATUS.md)** ⭐️
   - データベース状況
   - 本番データ vs モックデータ
   - セキュリティポリシー

### その他ドキュメント
- **[documents/](documents/)** - 詳細技術資料、過去のレポート
- **[DEMO_SCRIPT_FINAL.md](DEMO_SCRIPT_FINAL.md)** - デモ実施手順
- **[IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md)** - 実装作業ログ

---

## 🔄 システムアーキテクチャ

### 処理フロー（5ステップ）

```
ユーザー入力
    ↓
STEP 1: 意図解析（qwen2:0.5b）0.5秒
    ↓
STEP 2: RAG検索（ChromaDB）0.3秒 ⚡️並列
STEP 3: DB照会（MySQL）0.8秒 ⚡️並列
    ↓
STEP 4: 提案生成（スキルベースマッチング）0.2秒
    ↓
STEP 5: 応答生成（gemma2:2b）2.5秒
    ↓
応答（合計: 4.3秒）
```

**並列処理**: STEP 2とSTEP 3を同時実行（async/await）

### ポート一覧

| サービス | ローカル | AWS |
|---------|---------|-----|
| フロントエンド（Streamlit） | 8501 | 8501 |
| バックエンド（FastAPI） | 8002 | 8002 |
| MySQL | 3306 | 3306（RDS） |
| Redis | 6380 | 6380（Docker） |
| ChromaDB | 8003 | 8003（Docker） |
| Ollama Light | 11433 | 11433（Docker） |
| Ollama Main | 11435 | 11435（Docker） |

---

## 🧪 テスト方法

### テスト質問集（Q1～Q6）

**Q1: 納期20分前に処理完了**
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```

**Q2: 移動元への影響分析**
```
配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?
```

**Q3: 業務間移動**
```
SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?
```

**Q4: 完了時刻予測**
```
SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか
```

**Q5: 工程別最適配置**
```
あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか
```

**Q6: 遅延リスク検出**
```
現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか
```

---

### ローカル環境でのAPIテスト

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe

# バックエンドAPIテスト（Q1～Q6）
python3 run_api_test.py
# 期待結果: 総合精度95.8%
```

---

### E2Eテスト（Playwright）⭐️

**フロントエンド（ブラウザ）の自動テスト**

```bash
# 全質問テスト（Q1, Q3-Q6）
python3 final_test_all.py
# 期待結果: 合格率 100%

# Q1→Q2連続テスト（会話履歴確認）
python3 test_q1_q2_continuous.py
# Q1の配置提案後、Q2で影響分析を確認

# 個別テスト
python3 test_frontend_with_playwright.py
# Q1のみを詳細テスト
```

**環境セットアップ**:
```bash
pip3 install playwright
playwright install chromium
```

**テスト内容**:
- チャット入力の自動化
- 応答待機（最大60秒）
- スクリーンショット自動撮影（`/tmp/final_QX.png`）
- キーワード検証
- 承認ボタンのクリックテスト
```

### デバッグモード

**デバッグ情報を確認したい場合**:
```
http://localhost:8501/?debug=1
```

**表示される情報**:
- 意図解析結果（Intent Type、Location、Process）
- 実行されたSQL文とレコード数
- RAG検索結果と類似度スコア
- スキルマッチング詳細
- 処理時間内訳

### AWS環境でのテスト

```bash
# ヘルスチェック
curl http://54.150.242.233:8002/api/v1/health

# チャット機能テスト
python3 << 'EOF'
import requests
response = requests.post(
    "http://54.150.242.233:8002/api/v1/chat/message",
    json={
        "message": "SSの新SS(W)が納期ギリギリです。最適配置を教えてください。",
        "context": {},
        "session_id": "test"
    },
    timeout=120
)
print("ステータス:", response.status_code)
if response.status_code == 200:
    data = response.json()
    if data.get('suggestion'):
        print("✅ 提案生成成功")
        changes = data['suggestion']['changes']
        print(f"配置変更: {len(changes)}件")
        for c in changes[:2]:
            print(f"  {c['from_process_name']} → {c['to_process_name']}")
EOF
```

---

## 📞 サポート・参考資料

### ログ確認

#### ローカル環境
```bash
# バックエンドログ
tail -f /tmp/aimee_backend.log

# Dockerログ
docker logs aimee-be-api-1 --tail=50
docker logs aimee-frontend --tail=50
```

#### AWS環境
```bash
# バックエンドログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=100"

# フロントエンドログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend --tail=100"
```

### システムリソース確認

```bash
# ローカル
docker stats

# AWS
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker stats --no-stream"
```

---

## 🎓 開発者向けクイックコマンド

### データベース操作

```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# データ件数確認
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) FROM operators;')
print(f'オペレータ: {result[0][\"COUNT(*)\"]}名')
"

# モック名確認
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT operator_name FROM operators LIMIT 5;')
for r in result:
    print(r['operator_name'])
"
```

### ChromaDB操作

```bash
# コレクション確認
python3 << 'EOF'
import chromadb
client = chromadb.HttpClient(host='localhost', port=8003)
collections = client.list_collections()
for col in collections:
    print(f'{col.name}: {col.count()}件')
EOF
```

### Ollama操作

```bash
# モデル一覧
docker exec aimee-be-ollama-light-1 ollama list
docker exec aimee-be-ollama-main-1 ollama list

# モデル追加ダウンロード
docker exec aimee-be-ollama-main-1 ollama pull gemma3:4b
```

---

## 📈 パフォーマンス指標

### 実測値（2025-10-24）

| 指標 | 目標 | 実績 |
|------|------|------|
| API応答速度 | <5秒 | 4.3秒 ✅ |
| API精度 | >90% | 100% ✅ |
| 同時接続数 | 50人 | 対応可能 ✅ |
| データベースクエリ時間 | <1秒 | 0.8秒 ✅ |

### 処理時間内訳

| ステップ | 処理内容 | 時間 |
|---------|---------|------|
| STEP 1 | 意図解析（qwen2:0.5b） | 0.5秒 |
| STEP 2 | RAG検索（ChromaDB） | 0.3秒 ⚡️並列 |
| STEP 3 | DB照会（MySQL） | 0.8秒 ⚡️並列 |
| STEP 4 | 提案生成（ロジック） | 0.2秒 |
| STEP 5 | 応答生成（gemma2:2b） | 2.5秒 |
| **合計** | | **4.3秒** |

**並列化効果**: STEP 2とSTEP 3を並列実行し、30%高速化

---

## 🔗 関連リソース

### リポジトリ
- **フロントエンド**: `/Users/umemiya/Desktop/erax/aimee-fe`
- **バックエンド**: `/Users/umemiya/Desktop/erax/aimee-be`
- **データベース**: `/Users/umemiya/Desktop/erax/aimee-db`

### 外部リソース
- **システム構成図**: [diagrams.net](https://app.diagrams.net/?splash=0#G1kBIJvslm_yRlK2QyCbrDwr9GZnJFTb3X)
- **全体概要**: [Notion](https://pouncing-attic-dd0.notion.site/24154d8b9bc0807c8dfbc7278e5655cf)

---

## 📅 更新履歴

### 2025-10-26 - 承認・否認機能のDB保存対応
- ✅ approval_history への完全対応
- ✅ Pydantic v2対応（model_dump）
- ✅ 承認・否認ボタンのDB登録成功
- ✅ RAG学習準備完了（承認/否認履歴の蓄積）
- ✅ テスト実施（承認2件、否認2件確認）

### 2025-10-24 (v2.0.0) - スキルベースマッチング
- ✅ 異なる工程間移動を実現（エントリ2 → エントリ1）
- ✅ スキルベースマッチングアルゴリズム実装
- ✅ 4階層のみの表記（拠点名削除）
- ✅ Pydanticスキーマ更新
- ✅ AWSデプロイスクリプト作成
- ✅ データベース状況ドキュメント作成
- ✅ ドキュメント整理（documentsフォルダ）
- ✅ QUICK_REFERENCE.md作成（このドキュメント）

### 2025-10-20 (v1.0.0) - API精度100%達成
- ✅ 業務間移動優先ロジック
- ✅ 会話履歴管理（ConversationStore）
- ✅ Q1～Q6全問100%達成

### 2025-10-17 - ハイブリッドRAG実装
- ✅ progress_snapshots 832件投入
- ✅ ChromaDB管理者ノウハウ12件投入
- ✅ 6種類のintent_type実装

---

## 🎯 次のステップ

### 実装済み（完了）
- ✅ スキルベースマッチング
- ✅ 異なる工程間移動
- ✅ API精度100%
- ✅ AWSデプロイ
- ✅ ドキュメント整備

### 今後の拡張候補
1. **認証機能**: ユーザーログイン実装
2. **WebSocket通知**: リアルタイム通知
3. **自動更新**: 2分間隔でデータポーリング
4. **実配置データ取得**: RealWorksとのAPI連携
5. **アラート実データ対応**: progress_snapshotsベースのアラート生成

---

**作成日**: 2025-10-24
**管理者**: 開発チーム
