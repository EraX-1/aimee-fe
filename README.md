# AIMEE - AI配置最適化システム

**AI-powered Manpower Intelligent Efficiency Engine**

トランスコスモス様の健保組合業務における人員配置を、AI技術を活用して自動化・効率化するシステムです。

**最終更新**: 2025-11-01
**バージョン**: 2.0.0

---

## 🎯 主要機能

- **9種類の意図分類**: ユーザーの質問を自動分類し、最適な応答を生成
- **ハイブリッドRAG**: 定性データ（管理者ノウハウ）と定量データ（進捗・スキル）を統合
- **スキルベースマッチング**: 異なる工程間の人員移動を実現
- **4階層配置管理**: 業務大分類 → 業務名 → OCR区分 → 工程名
- **リアルタイム提案**: 納期・遅延リスクに基づく配置変更を提案

---

## 🚀 クイックスタート

### ローカル環境（⭐推奨: Docker起動スクリプト使用）

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

**メリット**: 全依存サービスが自動起動、本番環境と同じ構成

**詳細**: [LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)

### AWS本番環境デプロイ

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./deploy-to-aws.sh
```

**詳細**: [AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md)

---

## 📊 技術スタック

### フロントエンド
- **Streamlit** - WebUI
- **Python 3.12**

### バックエンド
- **FastAPI** - APIフレームワーク
- **Pydantic v2** - データバリデーション
- **SQLAlchemy 2.0** - 非同期ORM

### AI/LLM
- **Ollama** - ローカルLLM実行環境
  - **gemma2:2b** - 意図解析（20億パラメータ）
  - **gemma3:4b** - 応答生成（40億パラメータ）
- **ChromaDB** - ベクトルDB

### データベース
- **MySQL 8.0** - メインDB
- **Redis 7.0** - キャッシュ

**詳細**: [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## 🎯 9つのIntent Types

| # | 種類 | 説明 |
|---|------|------|
| 1 | `deadline_optimization` | 納期ベース最適化 |
| 2 | `completion_time_prediction` | 完了時刻予測 |
| 3 | `delay_risk_detection` | 遅延リスク検出 |
| 4 | `impact_analysis` | 影響分析 |
| 5 | `cross_business_transfer` | 業務間移動 |
| 6 | `process_optimization` | 工程別最適化 |
| 7 | `delay_resolution` | 遅延解消 |
| 8 | `status_check` | 状況確認 |
| 9 | `general_inquiry` | 一般質問 |

**詳細**: [INTENT_TYPES.md](docs/INTENT_TYPES.md)

---

## 🧪 テスト

### E2E自動テスト（Playwright）

**Q1〜Q6全質問を自動テスト**:

```bash
# ローカル環境テスト
cd /Users/umemiya/Desktop/erax/aimee-fe
python3 test/test_all_questions.py

# AWS環境テスト
python3 test/test_aws_all_questions.py
```

**実行内容**:
- ブラウザ自動起動
- Q1〜Q6を順番に入力
- 応答を確認
- スクリーンショット撮影（/tmp/）

**必要な環境**:
```bash
pip3 install playwright
playwright install chromium
```

---

## 🧪 テスト質問例（Q1～Q6）

### Q1: 納期20分前に処理完了
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```

### Q2: 移動元への影響分析
```
配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?
```

### Q3: 業務間移動
```
SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?
```

### Q4: 完了時刻予測
```
SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか
```

### Q5: 工程別最適配置
```
あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか
```

### Q6: 遅延リスク検出
```
現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか
```

---

## 📚 ドキュメント

### 必読ドキュメント

| ドキュメント | 説明 |
|------------|------|
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | システムアーキテクチャ、技術解説 |
| **[INTENT_TYPES.md](docs/INTENT_TYPES.md)** | 9分類の詳細、内部ロジック、具体例 |
| **[DATABASE_SETUP.md](docs/DATABASE_SETUP.md)** | DBセットアップ、ダミー/本番データ投入 |
| **[LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md)** | ローカル起動方法 |
| **[AWS_DEPLOYMENT.md](docs/AWS_DEPLOYMENT.md)** | AWSデプロイ方法 |
| **[CLAUDE.md](CLAUDE.md)** | AI用プロジェクトコンテキスト |

---

## 🌐 環境情報

### ローカル開発環境
- **フロントエンド**: http://localhost:8501
- **バックエンドAPI**: http://localhost:8002
- **APIドキュメント**: http://localhost:8002/docs

### AWS本番環境
- **フロントエンド**: http://43.207.175.35:8501
- **バックエンドAPI**: http://54.150.242.233:8002
- **APIドキュメント**: http://54.150.242.233:8002/docs

---

## 📈 パフォーマンス

- **処理時間**: 約4.3秒（並列化により30%短縮）
- **API精度**: 95.8%（最新テスト結果）
- **データ件数**:
  - progress_snapshots: 832件
  - operators: 100名（ダミーデータ）
  - ChromaDB: 12件

---

## 🔒 セキュリティ

- **ローカルLLM使用**: データ外部流出なし
- **実名データ保護**: 本番環境のみ、ローカルはモック名
- **環境変数管理**: 機密情報は.envで管理

---

## 📁 プロジェクト構成

```
aimee-fe/
├── frontend/                # Streamlitアプリ
│   ├── app.py              # メインアプリ
│   └── src/
│       ├── components/     # UIコンポーネント
│       └── utils/          # ユーティリティ
├── docs/                    # ドキュメント
│   ├── ARCHITECTURE.md     # システムアーキテクチャ
│   ├── INTENT_TYPES.md     # 9分類の詳細
│   ├── DATABASE_SETUP.md   # DBセットアップ
│   ├── LOCAL_DEVELOPMENT.md # ローカル起動方法
│   ├── AWS_DEPLOYMENT.md   # AWSデプロイ方法
│   ├── CHANGELOG.md        # 変更履歴
│   ├── IMPLEMENTATION_LOG.md # 実装ログ
│   └── DEMO_SCRIPT_FINAL.md # デモスクリプト
├── test/                    # E2Eテスト（Playwright）
│   ├── test_all_questions.py # Q1〜Q6自動テスト（ローカル）
│   ├── test_aws_all_questions.py # Q1〜Q6自動テスト（AWS）
│   └── api_test_results.json # 最新テスト結果
├── sandbox/                 # その他テストスクリプト
│   ├── run_api_test.py     # APIテスト
│   └── ...                 # その他
├── scripts/                 # 開発用スクリプト
│   ├── start_all.sh        # Python直接実行（全体）
│   ├── start_backend.sh    # Python直接実行（BE）
│   └── start_frontend.sh   # Python直接実行（FE）
├── docker-start-all.sh      # Docker起動（全体）⭐推奨
├── docker-start-backend.sh  # Docker起動（BE）⭐推奨
├── docker-start-frontend.sh # Docker起動（FE）⭐推奨
├── docker-stop-all.sh       # Docker停止
├── docker-check-status.sh   # Docker状態確認
├── deploy-to-aws.sh         # AWSデプロイ
├── CLAUDE.md               # AI用コンテキスト
└── README.md               # このファイル
```

---

## 🔧 トラブルシューティング

### バックエンドに接続できない
```bash
curl http://localhost:8002/api/v1/health
```

### データが表示されない
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) FROM operators')
print(f'operators: {result[0][\"COUNT(*)\"]}件')
"
```

**期待値**: 100件

不足している場合:
```bash
./restore_dummy_data.sh
```

詳細: [LOCAL_DEVELOPMENT.md - トラブルシューティング](docs/LOCAL_DEVELOPMENT.md#トラブルシューティング)

---

## 📝 ライセンス

内部プロジェクト - 非公開

---

## 👥 開発チーム

トランスコスモス様向けAI配置最適化プロジェクト
