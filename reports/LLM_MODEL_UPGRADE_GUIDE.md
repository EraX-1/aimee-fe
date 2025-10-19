# LLMモデルアップグレードガイド: gemma3:4b → gemma3:12b

**作成日**: 2025-10-16
**対象**: AIMEEバックエンドのLLMモデル変更

---

## 📋 現在のモデル構成

### 2つのOllamaコンテナで動作中

| コンテナ | モデル | 用途 | メモリ |
|---------|--------|------|--------|
| **ollama-light** | qwen2:0.5b | 意図解析 (軽量・高速) | 3GB |
| **ollama-main** | gemma3:4b | メイン処理・応答生成 | 12GB |

**ポート**:
- ollama-light: `11433` → `11434` (コンテナ内)
- ollama-main: `11435` → `11434` (コンテナ内)

---

## 🔧 モデルを gemma3:12b にアップグレードする方法

### 方法1: .envファイルを編集 (推奨)

**ファイル**: `/Users/umemiya/Desktop/erax/aimee-be/.env`

```bash
# 現在の設定
MAIN_MODEL=gemma3:4b    # メイン統合判断（Gemma 4Bパラメータ - 軽量モデル）

# ↓ 変更後
MAIN_MODEL=gemma3:12b   # メイン統合判断（Gemma 12Bパラメータ - 高性能モデル）
```

**変更手順**:
```bash
cd /Users/umemiya/Desktop/erax/aimee-be

# .envファイルを編集
vim .env
# または
code .env

# 21行目あたりの以下を変更:
# INTENT_MODEL=qwen2:0.5b          # そのまま
# ↓
# MAIN_MODEL=gemma3:12b            # 4b → 12b に変更
```

---

### 方法2: docker-compose.ymlを編集

**ファイル**: `/Users/umemiya/Desktop/erax/aimee-be/docker-compose.yml`

```yaml
# 155行目あたり
api:
  environment:
    INTENT_MODEL: qwen2:0.5b
    MAIN_MODEL: gemma3:12b    # ← ここを変更
```

---

## 🚀 モデル変更後の起動手順

### ステップ1: 現在のコンテナを停止

```bash
cd /Users/umemiya/Desktop/erax/aimee-be
docker-compose down
```

### ステップ2: ollama-mainコンテナを起動してモデルをダウンロード

```bash
# ollama-mainコンテナのみ起動
docker-compose up -d ollama-main

# コンテナに入る
docker exec -it aimee-be-ollama-main-1 bash

# gemma3:12bをダウンロード (約7GB、10-15分かかります)
ollama pull gemma3:12b

# ダウンロード完了後、モデル一覧を確認
ollama list

# 以下のように表示されればOK:
# NAME                ID              SIZE    MODIFIED
# gemma3:12b         abc123def456    7.0 GB  2 minutes ago
# gemma3:4b          def456ghi789    2.8 GB  3 days ago

# コンテナから出る
exit
```

### ステップ3: 全体を再起動

```bash
# 全コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f api

# 以下のようなログが出ればOK:
# INFO: Ollama URLs - Light: http://ollama-light:11434, Main: http://ollama-main:11434
# INFO: Using model: gemma3:12b
```

### ステップ4: 動作確認

```bash
# APIにアクセスして確認
curl http://localhost:8002/docs

# チャットAPIをテスト
curl -X POST "http://localhost:8002/api/v1/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "札幌のエントリ1が遅延しています",
    "context": {},
    "detail": false
  }'
```

---

## 📊 gemma3:4b vs gemma3:12b の比較

| 項目 | gemma3:4b | gemma3:12b |
|------|-----------|-----------|
| **パラメータ数** | 40億 | 120億 |
| **モデルサイズ** | 約2.8GB | 約7GB |
| **メモリ使用量** | 4-6GB | 8-12GB |
| **推論速度** | 速い (1-2秒) | 中程度 (3-5秒) |
| **精度** | 中 | 高 |
| **日本語対応** | 良好 | 優秀 |
| **複雑な推論** | やや弱い | 強い |

---

## ⚠️ 注意事項

### 1. メモリ要件

gemma3:12bは **最低12GB**、推奨16GBのメモリが必要です。

**現在のdocker-compose.yml設定**:
```yaml
ollama-main:
  environment:
    - OLLAMA_MEMORY_LIMIT=12GB
  deploy:
    resources:
      limits:
        memory: 12G
```

**推奨設定** (16GBに増やす):
```yaml
ollama-main:
  environment:
    - OLLAMA_MEMORY_LIMIT=16GB
  deploy:
    resources:
      limits:
        memory: 16G
```

### 2. 推論速度

- **4b**: 1-2秒で応答
- **12b**: 3-5秒で応答

ユーザー体験に影響する可能性があります。

### 3. ディスク容量

gemma3:12bのダウンロードには約7GBの空き容量が必要です。

```bash
# 空き容量を確認
df -h

# Docker volumeの容量を確認
docker system df -v
```

---

## 🎯 推奨設定

### 開発環境 (ローカルMac)

**メモリが16GB以上の場合**:
```bash
MAIN_MODEL=gemma3:12b
```

**メモリが16GB未満の場合**:
```bash
MAIN_MODEL=gemma3:4b  # 現状維持
```

### 本番環境 (AWS EC2等)

**推奨スペック**:
- インスタンスタイプ: `g4dn.xlarge` (GPU付き) または `r5.xlarge` (メモリ最適化)
- メモリ: 32GB以上
- モデル: `gemma3:12b`

---

## 📂 関連ファイル一覧

| ファイル | 設定内容 |
|---------|---------|
| `/aimee-be/.env` | `MAIN_MODEL=gemma3:4b` (21行目) |
| `/aimee-be/docker-compose.yml` | `MAIN_MODEL: gemma3:4b` (155行目) |
| `/aimee-be/app/core/config.py` | `MAIN_MODEL: str = Field(default="gemma3:4b-instruct")` (39行目) |
| `/aimee-be/app/services/ollama_service.py` | モデル使用箇所 |

---

## 🔍 トラブルシューティング

### Q1: gemma3:12bのダウンロードが遅い

**A**: 大きいファイルのため10-15分かかります。バックグラウンドでダウンロードしてください。

```bash
# ダウンロード状況を確認
docker exec -it aimee-be-ollama-main-1 ollama list
```

### Q2: メモリ不足エラーが出る

**A**: docker-compose.ymlのメモリ制限を増やしてください。

```yaml
ollama-main:
  deploy:
    resources:
      limits:
        memory: 16G  # 12G → 16G
```

### Q3: 古いモデル(4b)を削除したい

**A**: 以下のコマンドで削除できます。

```bash
docker exec -it aimee-be-ollama-main-1 bash
ollama rm gemma3:4b
exit
```

### Q4: 応答が遅くなった

**A**: これは正常です。12bは4bの3倍の推論時間がかかります。
- フロントエンドにローディング表示を強化
- ストリーミング応答を有効化 (`.env`で`STREAMING_RESPONSE=true`)

---

## ✅ チェックリスト

### モデル変更前
- [ ] 現在のメモリ使用量を確認 (`docker stats`)
- [ ] ディスク空き容量を確認 (最低10GB)
- [ ] 現在のモデルをバックアップ (必要に応じて)

### モデル変更中
- [ ] `.env`ファイルを編集
- [ ] docker-composeを停止
- [ ] gemma3:12bをダウンロード
- [ ] docker-composeを再起動

### モデル変更後
- [ ] APIが正常に起動することを確認
- [ ] チャットAPIの動作テスト
- [ ] 応答速度を確認
- [ ] メモリ使用量を監視

---

**レポート終了**

---

## 📌 クイックコマンド集

```bash
# 1. モデル変更
cd /Users/umemiya/Desktop/erax/aimee-be
vim .env  # MAIN_MODEL=gemma3:12b に変更

# 2. コンテナ停止
docker-compose down

# 3. ollama-main起動してモデルダウンロード
docker-compose up -d ollama-main
docker exec -it aimee-be-ollama-main-1 ollama pull gemma3:12b

# 4. 全体再起動
docker-compose up -d

# 5. 確認
docker-compose logs -f api | grep "Using model"
curl http://localhost:8002/docs
```
