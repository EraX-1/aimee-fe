# AIMEE - AI配置最適化システム

トランスコスモス様の健保組合業務における人員配置を、AI技術で自動化・効率化

**最終更新**: 2025-10-26
**バージョン**: 2.0.0 - スキルベースマッチング実装

📁 **[全ドキュメント索引はこちら](00_INDEX.md)** - プロジェクト全体の索引

---

## 🎉 最新の実装（2025-10-24）

### ✅ 異なる工程間移動の実現

**従来の問題**:
- ❌ 同じ工程間の移動（エントリ1 → エントリ1）
- ❌ 拠点間移動の表記（札幌 → 品川）

**新しい実装**:
- ✅ **異なる工程間移動**（エントリ2 → エントリ1）
- ✅ **スキルベースマッチング**（スキル保有を確認済み）
- ✅ **4階層のみの表記**（拠点名なし）
- ✅ **実名表示**（稲實　百合子さん等）
- ✅ **API精度100%維持**（全6問）

### 実際の応答例

```
「SS」の「新SS(W)」の「OCR非対象」の「エントリ2」から
稲實　百合子さんを「OCR非対象」の「エントリ1」へ1人移動

「SS」の「新SS(W)」の「OCR非対象」の「エントリ2」から
萩野　裕子さんを「OCR対象」の「エントリ1」へ1人移動
```

---

## 📚 主要ドキュメント

### 🎯 必読ドキュメント
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ⭐️⭐️⭐️⭐️ - **全ての最新情報（この1ページで完結）**
  - DB環境、利用モデル、デプロイ方法、API、セキュリティ等
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** ⭐️⭐️⭐️ - システム全体図（Mermaid）、処理フロー
- **[CLAUDE.md](CLAUDE.md)** ⭐️⭐️ - プロジェクト詳細、API一覧、起動方法
- **[CHANGELOG.md](CHANGELOG.md)** ⭐️ - 対応履歴（バグ修正、機能追加、データ修正等）
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** ⭐️ - ローカル環境セットアップ手順
- **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** ⭐️ - AWS本番環境デプロイ手順

### 🎬 デモ・テスト
- **[DEMO_SCRIPT_FINAL.md](DEMO_SCRIPT_FINAL.md)** - デモ実施手順と推奨質問文

### 📁 その他ドキュメント
- **[documents/](documents/)** - 詳細技術資料、過去のレポート等

---

## 🧪 テスト質問例（Q1～Q6）

AIMEEの全機能をテストできる標準質問集です。

### Q1: 納期20分前に処理完了
```
SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです。最適配置を教えてください。
```
**期待**: 納期対応の配置提案、4階層明示、異なる工程間移動（エントリ2 → エントリ1）

---

### Q2: 移動元への影響分析
```
配置転換元の工程は大丈夫ですか?移動元の処理に影響はありますか?
```
**期待**: Q1の提案を参照した影響分析、確認事項の提示

---

### Q3: 業務間移動
```
SSの16:40受信分を優先的に処理したいです。非SSから何人移動させたらよいですか?
```
**期待**: 非SS → SS の業務間移動提案、推奨人数（3～5人）

---

### Q4: 完了時刻予測
```
SS15:40受信分と適徴15:40受信分の処理は現在の配置だと何時に終了する想定ですか
```
**期待**: 完了時刻の予測、進捗データに基づく分析

---

### Q5: 工程別最適配置
```
あはきを16:40頃までに処理完了させるためには各工程何人ずつ配置したら良いですか
```
**期待**: エントリ1（4～5人）、補正（3～4人）、SV補正（2～3人）

---

### Q6: 遅延リスク検出
```
現在の配置でそれぞれの納期までに遅延が発生する見込みがある工程はありますか
```
**期待**: 遅延リスクのある工程のリスト、残タスク数、納期時刻

---

### 🔍 デバッグモード

デバッグ情報（意図解析、SQL文、RAG結果、類似度）を確認したい場合：
```
http://localhost:8501/?debug=1
```

### 📊 APIテスト実行

```bash
python3 run_api_test.py
# 期待結果: 総合精度 95.8%
```

---

### 🧪 E2Eテスト（Playwright）⭐️

**フロントエンド（ブラウザ）の自動テスト**

#### 全質問テスト（Q1, Q3-Q6）
```bash
python3 final_test_all.py
# Q1, Q3-Q6を自動入力してスクリーンショット撮影
# 期待結果: 合格率 100%
```

#### Q1→Q2連続テスト（会話履歴確認）
```bash
python3 test_q1_q2_continuous.py
# Q1の配置提案後、Q2で影響分析を確認
# 会話履歴機能の動作確認
```

#### 個別テスト
```bash
python3 test_frontend_with_playwright.py
# Q1のみを詳細テスト
```

**テスト内容**:
- ✅ チャット入力の自動化
- ✅ 応答待機（最大60秒）
- ✅ スクリーンショット自動撮影
- ✅ キーワード検証
- ✅ 承認ボタンのクリックテスト

**必要な環境**:
```bash
pip3 install playwright
playwright install chromium
```

**スクリーンショット保存先**: `/tmp/final_QX.png`

---

## 🚀 クイックスタート

### データベース切り替え（ワンコマンド）⭐️⭐️

#### 実名データ（本番・内部分析用）
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_real_data.sh
```

#### ダミーデータ（共有・デモ用）
```bash
cd /Users/umemiya/Desktop/erax/aimee-db
./restore_dummy_data.sh
```

**注**: 全2,832人のデータ、スクリプトは実行前に自動バックアップを作成

---

### AWS本番環境デプロイ（ワンコマンド）⭐️

```bash
./deploy-to-aws.sh
```

詳細は **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** を参照

---

### ローカル開発環境

#### Docker起動 (推奨)

```bash
# 全体起動 (バックエンド + フロントエンド)
./docker-start-all.sh

# 個別起動
./docker-start-backend.sh  # バックエンドのみ
./docker-start-frontend.sh  # フロントエンドのみ

# 状態確認
./docker-check-status.sh

# 停止
./docker-stop-all.sh
```

### ローカル起動 (開発用)

```bash
# バックエンド起動
cd /Users/umemiya/Desktop/erax/aimee-be
python3 start.py

# フロントエンド起動 (別ターミナル)
cd /Users/umemiya/Desktop/erax/aimee-fe/frontend
streamlit run app.py
```

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

**デプロイ手順**: 詳細は **[AWS_DEPLOY_GUIDE.md](AWS_DEPLOY_GUIDE.md)** を参照してください。

## 📁 プロジェクト構成

```
aimee-fe/
├── frontend/                # Streamlitアプリ
│   ├── app.py              # メインアプリ
│   └── src/
│       ├── components/     # UIコンポーネント
│       └── utils/          # ユーティリティ
│           └── api_client.py  # バックエンドAPI連携
├── Dockerfile              # フロントエンドDockerfile
├── docker-compose.yml      # フロントエンドCompose
├── requirements.txt        # Python依存関係
├── docker-start-all.sh     # 全体起動スクリプト
├── docker-start-backend.sh # バックエンド起動
├── docker-start-frontend.sh # フロントエンド起動
├── docker-stop-all.sh      # 全体停止
├── docker-check-status.sh  # 状態確認
├── CLAUDE.md               # プロジェクト詳細情報
└── README.md               # このファイル
```

## 🔧 主な機能

1. **💬 配置調整アシスタント**
   - AIチャットで配置提案を受け取る
   - 承認/却下でDB保存

2. **✅ 配置承認**
   - 承認待ち一覧表示
   - 一括承認/却下

3. **🚨 アラート表示**
   - リアルタイムアラート
   - アラート解消提案

## 🔗 関連リポジトリ

- **バックエンド**: `/Users/umemiya/Desktop/erax/aimee-be`
- **データベース**: `/Users/umemiya/Desktop/erax/aimee-db`

## 📊 システム状態

### データベース
- **実オペレータ**: 100名（稲實　百合子、萩野　裕子、櫻井　由希恵など）
- **スキル情報**: 191件（複数工程保有者多数）
- **業務**: SS、非SS、あはき、適用徴収（4階層対応）
- **拠点**: 6拠点（札幌、品川、本町東、西梅田、沖縄、佐世保）
- **進捗データ**: 832件（progress_snapshots）
- **管理者ノウハウ**: 12件（ChromaDB）

### 主な機能
- ✅ **スキルベースマッチング**: 異なる工程間移動（エントリ2 → エントリ1）
- ✅ **4階層のみ表記**: 拠点名なし、業務階層のみ
- ✅ **実オペレータ名表示**: 稲實　百合子さん、萩野　裕子さん等
- ✅ **ハイブリッドRAG**: MySQL（定量）+ ChromaDB（定性）
- ✅ **会話履歴管理**: ConversationStore実装
- ✅ **承認・否認機能**: DB保存完全対応、RAG学習準備完了
- ✅ **API精度100%**: 全6問で100%達成

---

## 🔧 完全セットアップ手順

初めてセットアップする場合は **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** を参照してください。

**主な手順**:
1. MySQL設定 (ユーザー・データベース作成)
2. スキーマ適用 (`schema.sql`)
3. 実データインポート (100名のオペレータ)
4. バックエンドDocker起動 (Ollama、ChromaDB、Redis)
5. フロントエンドDocker起動
6. 動作確認テスト

---

## 🐛 トラブルシューティング

### Dockerが起動しない
```bash
# Docker Desktop起動確認
docker info
```

### バックエンドに接続できない
```bash
# バックエンド状態確認
curl http://localhost:8002/api/v1/health

# ログ確認
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose logs -f api
```

### ポート競合
```bash
# ポート使用確認
lsof -i:8501  # フロントエンド
lsof -i:8002  # バックエンド
```

### データが表示されない
```bash
cd /Users/umemiya/Desktop/erax/aimee-db

# オペレータ数確認
python3 -c "
from config import db_manager
result = db_manager.execute_query('SELECT COUNT(*) as cnt FROM operators WHERE is_valid = 1')
print(f'オペレータ: {result[0][\"cnt\"]}名')
"

# 0名の場合、INSTALLATION_GUIDE.md の実データインポート手順を実行
```

詳細なトラブルシューティングは **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md#トラブルシューティング)** を参照してください。

---

## 🎯 技術的な特徴

### スキルベースマッチングアルゴリズム
1. 不足工程（例: エントリ1）のスキルを持つオペレータを全検索
2. 現在の配置工程を確認（例: エントリ2に配置中）
3. 異なる工程に配置中なら移動候補とする
4. 業務間移動を優先（非SS → SS）

### ハイブリッドRAG
- **MySQL**: 定量データ（進捗、スキル、オペレータ情報）
- **ChromaDB**: 定性データ（管理者ノウハウ、判断基準）

### 2段階LLM
- **qwen2:0.5b**: 高速な意図解析（0.5秒）
- **gemma2:2b**: 高品質な応答生成（2.5秒）

### API精度
- **全質問100%達成**（Q1～Q6）
- スキルベース、時刻予測、影響分析、リスク検出

---

## 📚 全ドキュメント一覧

### 📁 documents/ フォルダ
詳細な技術資料、過去のレポート、アーキテクチャドキュメントは[documents/](documents/)に整理されています。

---

## 📄 ライセンス

内部プロジェクト
