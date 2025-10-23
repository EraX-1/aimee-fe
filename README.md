# AIMEE フロントエンド

AI配置最適化システムのフロントエンドアプリケーション (Streamlit)

---

## 📚 ドキュメント

### 🔰 初めての方へ
- **[完全インストールガイド](INSTALLATION_GUIDE.md)** - フロント・バックエンド・DBの完全セットアップ手順
- **[デモ動画用台本](DEMO_SCRIPT_FINAL.md)** - デモ実施手順と推奨質問文

### 📖 詳細情報
- **[プロジェクト詳細](CLAUDE.md)** - システム構成、API一覧、統合状況
- **[技術要素まとめ](TECHNICAL_SUMMARY.md)** - 技術スタック、性能、構成図
- **[業務階層構造](BUSINESS_HIERARCHY.md)** - SS/非SS/あはき/適用徴収の4階層
- **[実データ成功レポート](REAL_DATA_SUCCESS.md)** - 実オペレータ100名での動作確認結果

---

## 🚀 クイックスタート

### Docker起動 (推奨)

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

### 現在のデータベース
- **実オペレータ**: 100名 (竹下朱美、高山麻由子、上野由香利など)
- **スキル情報**: 191件
- **業務**: SS、非SS、あはき、適用徴収 (4階層対応)
- **拠点**: 札幌、品川、本町東、西梅田、沖縄、佐世保

### 主な機能
- ✅ **4階層明示**: 「SS」の「新SS(W)」の「OCR対象」の「エントリ1」形式
- ✅ **実オペレータ名表示**: 萩野裕子さん、大川千代美さん など
- ✅ **配置転換提案**: AI信頼度85%
- ✅ **承認履歴保存**: 別システムから読み取り可能

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

## 📚 全ドキュメント一覧

### セットアップ関連
- **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** - 完全インストール手順（ローカル開発環境）
- **[AWS_DEPLOY_GUIDE.md](AWS_DEPLOY_GUIDE.md)** - AWS本番環境デプロイ手順 ⭐️

### 開発・運用関連
- **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - システムアーキテクチャ詳解（Mermaid図付き）⭐️
- **[CLAUDE.md](CLAUDE.md)** - プロジェクト詳細、API一覧、統合状況
- **[TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)** - 技術スタック、パフォーマンス
- **[INTEGRATION.md](INTEGRATION.md)** - フロント・バックエンド統合ガイド
- **[COMPLETE.md](COMPLETE.md)** - 完了作業記録

### デモ・テスト関連
- **[DEMO_SCRIPT_FINAL.md](DEMO_SCRIPT_FINAL.md)** - デモ動画用台本
- **[DEMO_QUESTIONS.md](DEMO_QUESTIONS.md)** - デモ用質問文パターン
- **[REAL_DATA_SUCCESS.md](REAL_DATA_SUCCESS.md)** - 実データテスト結果
- **[BUSINESS_HIERARCHY.md](BUSINESS_HIERARCHY.md)** - 業務階層構造

---

## 📄 ライセンス

内部プロジェクト
