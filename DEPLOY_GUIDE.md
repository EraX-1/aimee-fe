# AIMEE AWSデプロイガイド

**最終更新**: 2025-10-24

---

## 🚀 クイックデプロイ

### 全体デプロイ（フロントエンド + バックエンド）

```bash
cd /Users/umemiya/Desktop/erax/aimee-fe
./deploy-to-aws.sh
```

**所要時間**: 約10-15分

---

### 個別デプロイ

#### フロントエンドのみ
```bash
./deploy-to-aws.sh frontend
```

#### バックエンドのみ
```bash
./deploy-to-aws.sh backend
```

---

## 📋 デプロイ内容

### 自動実行される処理

1. **SSH接続確認**
   - SSHキー権限設定（chmod 400）
   - フロントエンド・バックエンドサーバーへの接続確認

2. **フロントエンドデプロイ**
   - ソースコードのアーカイブ作成
   - EC2への転送
   - 既存コンテナ停止
   - 新コード展開
   - docker-compose.yml設定（プラットフォーム: amd64）
   - コンテナビルド・起動
   - 動作確認

3. **バックエンドデプロイ**
   - ソースコードのアーカイブ作成
   - EC2への転送
   - 既存コンテナ停止
   - 新コード展開
   - .env設定（RDS接続）
   - docker-compose.yml設定（プラットフォーム: amd64）
   - 全サービス起動（API, Ollama, ChromaDB, Redis, MySQL）
   - ヘルスチェック

4. **動作確認テスト**
   - APIヘルスチェック
   - チャット機能テスト（スキルベースマッチング）
   - フロントエンドアクセステスト

---

## 🌐 本番環境URL

- **フロントエンド**: http://43.207.175.35:8501
- **バックエンドAPI**: http://54.150.242.233:8002
- **API Docs**: http://54.150.242.233:8002/docs

---

## ⚙️ 設定情報

### EC2インスタンス

| 項目 | フロントエンド | バックエンド |
|------|--------------|-------------|
| IP | 43.207.175.35 | 54.150.242.233 |
| SSHキー | ~/.ssh/aimee-key.pem | ~/.ssh/aimee-key.pem |
| ユーザー | ubuntu | ubuntu |
| ディレクトリ | ~/aimee-fe | ~/aimee-be |

### RDS MySQL
- **エンドポイント**: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com:3306
- **ユーザー**: admin
- **パスワード**: Aimee2024!RDS
- **データベース**: aimee_db

---

## 📊 デプロイ後の確認項目

### 1. コンテナ起動確認

```bash
# フロントエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 "docker ps"

# バックエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 "docker ps"
```

### 2. ログ確認

```bash
# フロントエンドログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend --tail=50"

# バックエンドAPIログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=50"
```

### 3. 機能テスト

```bash
# ヘルスチェック
curl http://54.150.242.233:8002/api/v1/health

# チャット機能テスト
curl -X POST http://54.150.242.233:8002/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message":"SSの新SS(W)が納期ギリギリです","context":{},"session_id":"test"}'
```

### 4. スキルベースマッチング確認

ブラウザで http://43.207.175.35:8501 にアクセスして：

1. チャット画面で「SSの新SS(W)が納期ギリギリのため納期20分前に処理完了となるよう配置したいです」と入力
2. 応答を確認：
   - ✅ 「エントリ2 → エントリ1」のような異なる工程間移動
   - ✅ 「SS」の「新SS(W)」の「OCR対象」の「エントリ1」形式（4階層）
   - ✅ 拠点名なし
   - ✅ 実名表示（稲實　百合子さん等）

---

## 🔧 トラブルシューティング

### デプロイスクリプトがエラーで停止

**症状**: SSH接続エラー
```
❌ フロントエンドサーバーに接続できません
```

**対処法**:
```bash
# SSHキー確認
ls -la ~/.ssh/aimee-key.pem

# 手動接続テスト
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35
```

---

### コンテナが起動しない

**症状**: docker psで表示されない

**対処法**:
```bash
# ログ確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=100"

# 手動再起動
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose restart"
```

---

### APIが応答しない

**症状**: ヘルスチェックが失敗

**対処法**:
```bash
# 依存サービスの確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker ps | grep aimee-be"

# Ollama起動確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker exec aimee-be-ollama-main-1 ollama list"

# RDS接続確認
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 | grep -i 'database\|rds'"
```

---

## 🔄 ロールバック

### 手動ロールバック

```bash
# バックエンド停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "cd ~/aimee-be && docker-compose down"

# フロントエンド停止
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "cd ~/aimee-fe && docker-compose down"
```

---

## 📝 デプロイ前チェックリスト

### ローカル環境で実施

- [ ] ローカルでAPI精度100%を確認（`python3 run_api_test.py`）
- [ ] バックエンドが起動している
- [ ] フロントエンドが起動している
- [ ] スキルベースマッチングが動作している

### デプロイ実施

- [ ] `./deploy-to-aws.sh` を実行
- [ ] エラーなく完了することを確認
- [ ] 本番環境URLにアクセス
- [ ] チャット機能をテスト

---

## 🎯 デプロイ後の確認ポイント

### 必須確認事項

1. **フロントエンド**
   - [ ] http://43.207.175.35:8501 にアクセスできる
   - [ ] チャット画面が表示される

2. **バックエンド**
   - [ ] http://54.150.242.233:8002/api/v1/health が "healthy"
   - [ ] http://54.150.242.233:8002/docs でAPIドキュメントが表示される

3. **スキルベースマッチング**
   - [ ] 異なる工程間移動が提案される（エントリ2 → エントリ1）
   - [ ] 4階層のみの表記（拠点名なし）
   - [ ] 実名が表示される

4. **全サービス起動**
   - [ ] API（FastAPI）
   - [ ] Ollama Light（qwen2:0.5b）
   - [ ] Ollama Main（gemma2:2b, gemma3:4b）
   - [ ] ChromaDB
   - [ ] Redis
   - [ ] MySQL

---

## 💡 Tips

### デプロイ時間の目安
- フロントエンドのみ: 約5分
- バックエンドのみ: 約10分
- 全体: 約15分

### バックグラウンド実行

```bash
# ログを見ながら実行
./deploy-to-aws.sh 2>&1 | tee deploy.log

# バックグラウンドで実行
nohup ./deploy-to-aws.sh > deploy.log 2>&1 &
```

### 特定バージョンのデプロイ

```bash
# 現在のブランチをデプロイ
git checkout main
./deploy-to-aws.sh

# 特定のコミットをデプロイ
git checkout <commit-hash>
./deploy-to-aws.sh
git checkout main  # 戻す
```

---

## 📞 サポート

### ログ収集コマンド

問題が発生した場合、以下のコマンドでログを収集：

```bash
# フロントエンドログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
    "docker logs aimee-frontend --tail=200" > frontend.log

# バックエンドAPIログ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker logs aimee-be-api-1 --tail=200" > backend-api.log

# 全コンテナ状態
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
    "docker ps -a" > containers.log
```

---

**最終更新**: 2025-10-24
