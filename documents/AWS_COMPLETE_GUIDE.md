# AIMEE AWS デプロイ完全ガイド

**最終更新**: 2025-10-10
**ステータス**: ✅ 本番稼働中

---

## 📋 目次

1. [アクセスURL](#アクセスurl)
2. [システム構成](#システム構成)
3. [AWS認証・ログイン](#aws認証ログイン)
4. [EC2操作コマンド](#ec2操作コマンド)
5. [データベースセットアップ](#データベースセットアップ)
6. [ログ確認](#ログ確認)
7. [デモ用質問文](#デモ用質問文)
8. [トラブルシューティング](#トラブルシューティング)
9. [コスト情報](#コスト情報)

---

## 🌐 アクセスURL

### フロントエンド (Streamlit)
```
http://43.207.175.35:8501
```
**PC・スマホどちらからでもアクセス可能**

### バックエンドAPI (Swagger UI)
```
http://54.150.242.233:8002/docs
```

---

## 🏗️ システム構成

### 1. RDS MySQL
- **エンドポイント**: `aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com`
- **スペック**: db.t3.medium (2vCPU, 4GB RAM)
- **ユーザー**: admin
- **パスワード**: Aimee2024!RDS
- **データベース**: aimee_db
- **データ**: オペレータ100名 (Mock名)、スキル191件

### 2. バックエンドEC2
- **IP**: `54.150.242.233`
- **インスタンスID**: `i-0fbda194ced01880a`
- **スペック**: **c6i.4xlarge** (16vCPU, 32GB RAM)
- **ディスク**: 50GB gp3
- **月額**: 約¥84,000 (スポット起動で¥21,000/月)

**Dockerコンテナ**:
| コンテナ | イメージ | ポート | 用途 |
|---------|---------|-------|------|
| aimee-be-api-1 | FastAPI | 8002 | メインAPI |
| aimee-be-ollama-main-1 | Ollama | 11435 | LLM (gemma2:2b-q4) |
| aimee-be-ollama-light-1 | Ollama | 11433 | LLM (qwen2:0.5b) |
| aimee-be-chromadb-1 | ChromaDB | 8003 | ベクトルDB |
| aimee-be-redis-1 | Redis | 6380 | キャッシュ |

### 3. フロントエンドEC2
- **IP**: `43.207.175.35`
- **インスタンスID**: `i-03b4b4c0fbc4ad722`
- **スペック**: t3.small (2vCPU, 2GB RAM)
- **月額**: 約¥2,280

**Dockerコンテナ**:
| コンテナ | ポート | 用途 |
|---------|-------|------|
| aimee-fe_frontend_1 | 8501 | Streamlit |

---

## 🔐 AWS認証・ログイン

### 1. AWS SSOログイン
```bash
# SSOログイン
aws sso login --profile aimee

# 認証確認
aws sts get-caller-identity --profile aimee
```

**出力例**:
```json
{
    "UserId": "AROAWOINM4SU5MXJHZJNQ:amemiya_yuichiro",
    "Account": "442946610345",
    "Arn": "arn:aws:sts::442946610345:assumed-role/..."
}
```

### 2. SSH接続
```bash
# バックエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233

# フロントエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35
```

---

## 🚀 EC2操作コマンド

### EC2起動・停止

#### バックエンドEC2起動
```bash
# 起動
aws ec2 start-instances --profile aimee --instance-ids i-0fbda194ced01880a

# 起動完了待機
aws ec2 wait instance-running --profile aimee --instance-ids i-0fbda194ced01880a

# IPアドレス確認
aws ec2 describe-instances --profile aimee \
  --instance-ids i-0fbda194ced01880a \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

#### バックエンドEC2停止
```bash
aws ec2 stop-instances --profile aimee --instance-ids i-0fbda194ced01880a
```

### Docker操作

#### バックエンドDocker起動
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
cd aimee-be
docker-compose up -d
EOF
```

#### バックエンドDocker停止
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
cd aimee-be
docker-compose down
EOF
```

#### フロントエンドDocker再起動
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 << 'EOF'
cd aimee-fe
docker-compose restart
EOF
```

### コンテナ状態確認

#### バックエンド
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
cd aimee-be
docker-compose ps
EOF
```

#### フロントエンド
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 << 'EOF'
cd aimee-fe
docker-compose ps
EOF
```

---

## 💾 データベースセットアップ

### ⚠️ 重要: 本番環境は必ずMock名データを使用

### 完全セットアップ手順

#### 1. ローカルDBから実データをエクスポート
```bash
cd /Users/umemiya/Desktop/erax/aimee-db

mysqldump -u root -h 127.0.0.1 aimee_db \
  operators operator_process_capabilities operator_work_records progress_snapshots login_records \
  --no-create-info --skip-add-locks --single-transaction \
  > /tmp/real_data_full.sql
```

#### 2. オペレータ名のみをMock名に置換
```bash
cd /Users/umemiya/Desktop/erax/aimee-db

python3 << 'PYTHON'
import re
import random

LAST_NAMES = ['佐藤', '鈴木', '高橋', '田中', '伊藤', '渡辺', '山本', '中村', '小林', '加藤',
              '吉田', '山田', '佐々木', '山口', '松本', '井上', '木村', '林', '斎藤', '清水',
              '山崎', '森', '池田', '橋本', '阿部', '石川', '前田', '藤田', '後藤', '岡田',
              '長谷川', '村上', '近藤', '石井', '坂本', '遠藤', '青木', '藤井', '西村', '福田',
              '太田', '三浦', '岡本', '藤原', '中島', '原田', '和田', '竹内', '野口', '古川']

FIRST_NAMES_M = ['太郎', '次郎', '三郎', '健', '誠', '剛', '勇', '学', '明', '浩', '豊',
                 '悠真', '蓮', '湊', '陽翔', '大翔', '颯真', '朝陽', '翔太', '拓海', '健太',
                 '翔', '大輝', '陽太', '一郎', '達也', '洋平', '修', '正', '和也', '淳']

FIRST_NAMES_F = ['花子', '和子', '明美', '幸子', '恵子', '由美', '久美子', '裕子', '悦子', '奈緒',
                 '結菜', '陽葵', '美月', '咲良', '心春', '美桜', '葵', 'さくら', '楓', '凛',
                 '詩織', '美咲', '優花', '彩花', '琴音', '瞳', '沙織', '美優', '柚希', '愛菜']

with open('/tmp/real_data_full.sql', 'r') as f:
    content = f.read()

name_map = {}

def get_mock_name():
    last = random.choice(LAST_NAMES)
    first = random.choice(FIRST_NAMES_M if random.random() > 0.5 else FIRST_NAMES_F)
    return f"{last}　{first}"

operator_pattern = r"INSERT INTO \`operators\`.*?VALUES\s+(.*?);"
new_content = content

for match in re.finditer(operator_pattern, content, re.DOTALL):
    for record in re.findall(r"\((.*?)\)", match.group(1)):
        fields = [f.strip().strip("'") for f in record.split("','")]
        if len(fields) >= 2:
            operator_id, real_name = fields[0].strip("'"), fields[1]
            if real_name not in name_map and not real_name.startswith('ﾏｸﾛﾏﾝ'):
                mock_name = get_mock_name()
                while mock_name in name_map.values():
                    mock_name = get_mock_name() + str(len([v for v in name_map.values() if mock_name in v]))
                name_map[real_name] = mock_name
            if real_name in name_map:
                new_content = new_content.replace(f"'{operator_id}','{real_name}'",
                                                  f"'{operator_id}','{name_map[real_name]}'")

with open('/tmp/real_data_masked.sql', 'w') as f:
    f.write(new_content)

print(f"✅ Mock名変換完了: {len(name_map)} 件")
for i, (real, mock) in enumerate(list(name_map.items())[:10]):
    print(f"{i+1}. {real} → {mock}")
PYTHON
```

#### 3. EC2経由でRDSにインポート
```bash
# EC2にアップロード
scp -i ~/.ssh/aimee-key.pem /tmp/real_data_masked.sql ubuntu@54.150.242.233:~/

# RDSにインポート
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
echo "🗑️ 既存データ削除..."
mysql -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  -u admin -p'Aimee2024!RDS' \
  aimee_db << SQL
    SET FOREIGN_KEY_CHECKS = 0;
    TRUNCATE TABLE operator_process_capabilities;
    TRUNCATE TABLE operator_work_records;
    TRUNCATE TABLE operators;
    TRUNCATE TABLE progress_snapshots;
    TRUNCATE TABLE login_records;
    SET FOREIGN_KEY_CHECKS = 1;
SQL

echo "📥 Mock名データインポート..."
mysql -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  -u admin -p'Aimee2024!RDS' \
  aimee_db < real_data_masked.sql

echo ""
echo "✅ インポート完了"
echo ""
echo "=== データ件数確認 ==="
mysql -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  -u admin -p'Aimee2024!RDS' \
  aimee_db << SQL
    SELECT 'operators' AS table_name, COUNT(*) AS count FROM operators
    UNION ALL
    SELECT 'operator_process_capabilities', COUNT(*) FROM operator_process_capabilities
    UNION ALL
    SELECT 'progress_snapshots', COUNT(*) FROM progress_snapshots;
SQL

echo ""
echo "=== Mock名確認 (ランダム10件) ==="
mysql -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  -u admin -p'Aimee2024!RDS' \
  aimee_db -e "SELECT operator_name FROM operators ORDER BY RAND() LIMIT 10;"
EOF
```

---

## 📊 ログ確認

### バックエンドAPIログ
```bash
# 最新50行
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker logs --tail 50 aimee-be-api-1"

# リアルタイム監視
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker logs -f aimee-be-api-1"

# エラーのみ
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker logs --tail 100 aimee-be-api-1 2>&1 | grep ERROR"
```

### Ollamaログ
```bash
# Ollama Main (gemma2:2b-q4)
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker logs --tail 50 aimee-be-ollama-main-1"

# Ollama Light (qwen2:0.5b)
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker logs --tail 50 aimee-be-ollama-light-1"
```

### フロントエンドログ
```bash
# 最新50行
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
  "docker logs --tail 50 aimee-fe_frontend_1"

# リアルタイム監視
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
  "docker logs -f aimee-fe_frontend_1"
```

### コンテナリソース使用状況
```bash
# バックエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'"

# フロントエンド
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 \
  "docker stats --no-stream"
```

---

## 🧪 デモ用質問文

### 基本的な遅延解決

#### 1. 拠点遅延
```
札幌のエントリ1工程が遅延しています
```

```
品川の補正工程が予定より遅れています
```

```
本町東のSV補正が30分遅延しています
```

#### 2. 業務別遅延
```
新SS(W)のエントリ1が処理しきれていません
```

```
非SS(片道)の補正工程を強化したい
```

### 配置相談

#### 3. 人員移動
```
佐世保から札幌にエントリ1の経験者を3名配置したい
```

```
品川拠点の人員を他拠点に振り分けたい
```

#### 4. スキル確認
```
エントリ1工程ができるオペレータは何人いますか?
```

```
SV補正のスキルを持つ人を教えてください
```

### 業務状況確認

#### 5. 進捗確認
```
今日の全体の進捗状況を教えて
```

```
各拠点の処理状況はどうですか?
```

```
遅延している業務を一覧で見せて
```

### 複雑な質問

#### 6. 最適化提案
```
明日の配置を最適化してください
```

```
全拠点でエントリ1を効率化する方法は?
```

```
品川の生産性を20%向上させたい
```

---

## 🔍 動作確認コマンド

### 1. ヘルスチェック
```bash
# バックエンド
curl -s http://54.150.242.233:8002/api/v1/health | python3 -m json.tool

# フロントエンド
curl -s -I http://43.207.175.35:8501 | head -3
```

### 2. チャットAPI
```bash
curl -X POST 'http://54.150.242.233:8002/api/v1/chat/message' \
  -H 'Content-Type: application/json' \
  -d '{"message": "札幌のエントリ1工程が遅延しています", "session_id": "test"}' \
  | python3 -m json.tool
```

### 3. アラート一覧
```bash
curl -s 'http://54.150.242.233:8002/api/v1/alerts' | python3 -m json.tool
```

### 4. 承認待ち一覧
```bash
curl -s 'http://54.150.242.233:8002/api/v1/approvals' | python3 -m json.tool
```

### 5. Mock名確認
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
mysql -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  -u admin -p'Aimee2024!RDS' \
  aimee_db -e "SELECT operator_name FROM operators ORDER BY RAND() LIMIT 10;"
EOF
```

**期待される出力** (Mock名):
- 佐藤　太郎
- 鈴木　花子
- 田中　湊

**❌ 絶対に出てはいけない**:
- 実際の個人名

---

## 🛠️ トラブルシューティング

### Q1: フロントエンドが「分析中...」から動かない

**原因**: バックエンドEC2が停止している、またはIPアドレスが変わった

**確認**:
```bash
# バックエンドの状態確認
aws ec2 describe-instances --profile aimee \
  --instance-ids i-0fbda194ced01880a \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress]' \
  --output table
```

**対処**:
```bash
# バックエンド起動
aws ec2 start-instances --profile aimee --instance-ids i-0fbda194ced01880a

# IPアドレス取得
NEW_IP=$(aws ec2 describe-instances --profile aimee \
  --instance-ids i-0fbda194ced01880a \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# フロントエンドのIPを更新
ssh -i ~/.ssh/aimee-key.pem ubuntu@43.207.175.35 << EOF
cd aimee-fe
sed -i "s/AIMEE_API_URL=http:\/\/.*:8002/AIMEE_API_URL=http:\/\/$NEW_IP:8002/" docker-compose.yml
docker-compose restart
EOF
```

### Q2: APIレスポンスが遅い (30秒以上)

**原因**: CPUインスタンスでLLMを実行している

**現状**: 23秒 (c6i.4xlarge)

**改善策**:
1. GPU搭載インスタンス (g4dn.xlarge) に変更 → 2-3秒
2. 軽量モデルに変更 (精度低下)
3. 非同期処理に変更

**GPU申請**:
```
AWS Console → Service Quotas → EC2 → "Running On-Demand G and VT instances"
```

### Q3: 実名がRDSに入ってしまった

**⚠️ 緊急対処**:
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
mysql -h aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com \
  -u admin -p'Aimee2024!RDS' \
  aimee_db << SQL
    SET FOREIGN_KEY_CHECKS = 0;
    TRUNCATE TABLE operators;
    TRUNCATE TABLE operator_process_capabilities;
    SET FOREIGN_KEY_CHECKS = 1;
SQL
echo "✅ 実名データ削除完了"
EOF

# その後、上記「データベースセットアップ」手順を実行
```

### Q4: Dockerコンテナが起動しない

**確認**:
```bash
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 << 'EOF'
cd aimee-be
docker-compose logs --tail 50
EOF
```

**よくある原因**:
- ディスク容量不足: `df -h` で確認
- メモリ不足: `free -h` で確認
- ポート競合: `docker-compose down && docker-compose up -d`

---

## 💰 コスト情報

### 月額コスト (オンデマンド)

| リソース | スペック | 月額 (JPY) |
|---------|---------|-----------|
| バックエンドEC2 | c6i.4xlarge | ¥84,000 |
| フロントエンドEC2 | t3.small | ¥2,280 |
| RDS MySQL | db.t3.medium | ¥9,750 |
| EBS | 80GB | ¥1,200 |
| **合計** | - | **¥97,230** |

### スポット起動 (推奨)

**使用例**: 1日8時間×月20日
- **時間単価**: ¥132/時間
- **1日**: ¥1,056
- **月額**: **¥21,120**

**節約額**: ¥97,230 - ¥21,120 = **¥76,110/月** (約78%削減)

### コスト削減コマンド
```bash
# 使用後は必ず停止
aws ec2 stop-instances --profile aimee --instance-ids i-0fbda194ced01880a

# 停止確認
aws ec2 describe-instances --profile aimee \
  --instance-ids i-0fbda194ced01880a \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text
```

---

## 📝 システム起動・停止フロー

### 起動フロー (所要時間: 約3分)

```bash
# 1. バックエンドEC2起動 (1分)
aws ec2 start-instances --profile aimee --instance-ids i-0fbda194ced01880a
aws ec2 wait instance-running --profile aimee --instance-ids i-0fbda194ced01880a

# 2. IPアドレス確認
aws ec2 describe-instances --profile aimee \
  --instance-ids i-0fbda194ced01880a \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text

# 3. Docker起動確認 (1分)
ssh -i ~/.ssh/aimee-key.pem ubuntu@54.150.242.233 \
  "cd aimee-be && docker-compose ps"

# 4. API疎通確認
curl -s http://54.150.242.233:8002/api/v1/health

# 5. ブラウザでアクセス
# http://43.207.175.35:8501
```

### 停止フロー (所要時間: 約1分)

```bash
# 1. バックエンドEC2停止
aws ec2 stop-instances --profile aimee --instance-ids i-0fbda194ced01880a

# 2. 停止確認
aws ec2 wait instance-stopped --profile aimee --instance-ids i-0fbda194ced01880a

echo "✅ 停止完了"
```

---

## 🔐 認証情報まとめ

### AWS
- **プロファイル**: `aimee`
- **アカウントID**: 442946610345
- **リージョン**: ap-northeast-1 (東京)

### RDS
- **ホスト**: aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com
- **ポート**: 3306
- **ユーザー**: admin
- **パスワード**: Aimee2024!RDS
- **データベース**: aimee_db

### SSH
- **鍵**: ~/.ssh/aimee-key.pem
- **ユーザー**: ubuntu
- **バックエンドIP**: 54.150.242.233
- **フロントエンドIP**: 43.207.175.35

---

## 📈 パフォーマンス

### APIレスポンス時間
- **初回**: 27秒 (モデルロード含む)
- **2回目以降**: **23秒**

### 構成
- **CPU**: c6i.4xlarge (16vCPU)
- **LLM**: gemma2:2b-instruct-q4_K_M (1.7GB)
- **並列**: 16スレッド

### 高速化オプション
- **GPU搭載**: g4dn.xlarge → **2-3秒** (要:制限緩和申請)

---

## 🎯 クイックスタート

### 1日の始め
```bash
# AWS認証
aws sso login --profile aimee

# バックエンド起動
aws ec2 start-instances --profile aimee --instance-ids i-0fbda194ced01880a
aws ec2 wait instance-running --profile aimee --instance-ids i-0fbda194ced01880a

# ブラウザでアクセス
open http://43.207.175.35:8501
```

### 1日の終わり
```bash
# バックエンド停止
aws ec2 stop-instances --profile aimee --instance-ids i-0fbda194ced01880a
```

---

## 📞 サポート情報

### 関連ドキュメント
- **DBセットアップ**: `/Users/umemiya/Desktop/erax/aimee-db/DB_SETUP_GUIDE.md`
- **プロジェクト情報**: `/Users/umemiya/Desktop/erax/aimee-fe/CLAUDE.md`
- **ローカル起動**: `CLAUDE.md` の「システム起動方法」参照

### リソースID一覧
| リソース | ID | 備考 |
|---------|----|----|
| バックエンドEC2 | i-0fbda194ced01880a | c6i.4xlarge |
| フロントエンドEC2 | i-03b4b4c0fbc4ad722 | t3.small (常時起動) |
| RDS | aimee-db.c96uew4c8z02.ap-northeast-1.rds.amazonaws.com | db.t3.medium |
| EBSボリューム | vol-0d63984222c1d81e6 | 50GB |
| セキュリティグループ | sg-0d3c973d445cd1011 | ポート8002,8501,22 |
| SSH鍵 | ~/.ssh/aimee-key.pem | chmod 400 |

---

## ⚠️ セキュリティ注意事項

### 現在の設定
- ⚠️ HTTPのみ (暗号化なし)
- ⚠️ 全IPからアクセス可能
- ⚠️ 認証なし
- ✅ Mock名使用 (個人情報保護)

### 本番運用時の推奨
1. **HTTPS化** (Let's Encrypt)
2. **特定IPのみ許可** (セキュリティグループ)
3. **VPN経由アクセス**
4. **Basic認証追加**

---

## 🎉 デプロイ完了チェックリスト

- [x] RDS作成・スキーマ投入
- [x] Mock名データ作成・インポート
- [x] バックエンドEC2起動 (c6i.4xlarge)
- [x] Docker起動・Ollamaモデルダウンロード
- [x] フロントエンドEC2起動 (t3.small)
- [x] API疎通確認
- [x] フロントエンド表示確認
- [x] Mock名確認 (個人情報保護)
- [x] 全APIエンドポイント動作確認
- [x] ドキュメント作成

---

**作成日**: 2025-10-10
**ステータス**: ✅ **本番稼働中** (Mock名データ)
**アクセスURL**: http://43.207.175.35:8501
