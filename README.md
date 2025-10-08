# AIMEE フロントエンド

AI配置最適化システムのフロントエンドアプリケーション (Streamlit)

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

- **フロントエンド**: http://localhost:8501
- **バックエンドAPI**: http://localhost:8002/docs
- **DB接続**: MySQL localhost:3306 (user: aimee_user, pass: Aimee2024!)

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

## 📝 詳細情報

詳細は `CLAUDE.md` を参照してください。

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

## 📄 ライセンス

内部プロジェクト
