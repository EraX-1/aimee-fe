# AWS セットアップ チェックリスト

## ✅ 完了した作業
- [x] AWS CLIインストール完了 (v2.31.10)

---

## 🔍 現在の状況

### AWSアクセスポータル
- **ログイン**: 成功 ✅
- **表示内容**: 「管理者からアプリケーションとAWSアカウントへのアクセス権が付与されたら、ここで確認できます」
- **問題**: AWSアカウント一覧が表示されていない ❌

**原因**: 管理者からまだアクセス権限が付与されていない

---

## 📋 次に必要なアクション

### 1. 管理者に権限付与を依頼する

管理者に以下のメッセージを送ってください:

```
件名: AWSアクセス権限の付与依頼

お世話になっております。

AIMEEシステムをAWSにデプロイするため、
以下のアクセス権限を付与いただけますでしょうか。

【必要な権限】
- EC2の作成・管理権限
- セキュリティグループの作成・管理
- Elastic IPの割り当て
- CloudWatch Logsへのアクセス

【推奨される権限セット】
- PowerUserAccess (推奨)
  または
- AdministratorAccess (一時的に全権限)

【使用リージョン】
- ap-northeast-1(東京リージョン)

【デプロイ内容】
- システム名: AIMEE (AI配置最適化システム)
- 使用サービス: EC2, CloudWatch
- 想定インスタンス: c6i.2xlarge
- 想定月額コスト: 約¥40,000

【目的】
- デモ・PoC環境のデプロイ
- 顧客プレゼンテーション用

よろしくお願いいたします。
```

---

### 2. 権限付与後の確認手順

管理者から「権限を付与した」と連絡があったら:

1. **AWSアクセスポータルを再読み込み**
   - ブラウザでリロード (Cmd + R)

2. **AWSアカウントが表示されるか確認**
   - 「AWS Account」という項目が表示される
   - アカウント名またはアカウントIDが表示される

3. **アカウントをクリック**
   - 「Management console」リンクが表示される
   - 「Command line or programmatic access」リンクが表示される

---

### 3. 認証情報の取得方法

権限付与後、以下の手順で認証情報を取得:

#### オプションA: AWS IAM Identity Center (SSO)

1. **AWSアクセスポータル**にログイン
2. 使用するAWSアカウントをクリック
3. **「Command line or programmatic access」**をクリック
4. 表示される認証情報をコピー

**表示される情報**:
```bash
# 環境変数として設定する方法
export AWS_ACCESS_KEY_ID="ASIAxxxxxxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxxxxxx"
export AWS_SESSION_TOKEN="xxxxxxxxxx"
export AWS_DEFAULT_REGION="ap-northeast-1"

# または ~/.aws/credentials に設定
[default]
aws_access_key_id = ASIAxxxxxxxxxx
aws_secret_access_key = xxxxxxxxxx
aws_session_token = xxxxxxxxxx
```

5. ターミナルで以下を実行:
```bash
# 環境変数として設定 (一時的)
export AWS_ACCESS_KEY_ID="ASIAxxxxxxxxxx"
export AWS_SECRET_ACCESS_KEY="xxxxxxxxxx"
export AWS_SESSION_TOKEN="xxxxxxxxxx"
export AWS_DEFAULT_REGION="ap-northeast-1"

# 動作確認
aws sts get-caller-identity
```

---

#### オプションB: IAMユーザー (従来型)

もし管理者が従来型のIAMユーザーを作成してくれた場合:

1. **Access Key IDとSecret Access Key**を受け取る
2. AWS CLIで設定:

```bash
aws configure

# 入力を求められる
AWS Access Key ID [None]: AKIAxxxxxxxxxx
AWS Secret Access Key [None]: xxxxxxxxxx
Default region name [None]: ap-northeast-1
Default output format [None]: json
```

3. 動作確認:
```bash
aws sts get-caller-identity
```

**正常な出力例**:
```json
{
    "UserId": "AIDxxxxxxxxxx",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-username"
}
```

---

## 🎯 認証設定完了後のデプロイフロー

認証情報が設定できたら、以下の順でデプロイします:

### Phase 1: EC2インスタンス作成
```bash
# SSH鍵ペア作成
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aimee-aws-key

# EC2インスタンス起動
# (自動スクリプトを使用)
```

### Phase 2: Docker環境構築
```bash
# EC2にSSH接続
# Dockerインストール
# Docker Composeインストール
```

### Phase 3: プロジェクトデプロイ
```bash
# aimee-fe, aimee-be, aimee-db をアップロード
# MySQLセットアップ
# バックエンド起動
# フロントエンド起動
```

### Phase 4: 動作確認
```bash
# APIヘルスチェック
# フロントエンドアクセス
# チャット機能テスト
```

---

## 💡 代替案: マネジメントコンソールから手動デプロイ

もしAWS CLIの設定がうまくいかない場合、ブラウザから手動でデプロイすることもできます。

### 手順

1. **AWSアクセスポータル**で「Management console」をクリック
2. **EC2ダッシュボード**に移動
3. **「インスタンスを起動」**ボタンをクリック
4. 以下を設定:
   - **名前**: `aimee-production`
   - **AMI**: Amazon Linux 2023
   - **インスタンスタイプ**: c6i.2xlarge
   - **キーペア**: 新規作成 (aimee-aws-key)
   - **ストレージ**: 100GB gp3
   - **セキュリティグループ**:
     - SSH (22番ポート)
     - HTTP (8501番ポート: Streamlit)
     - HTTP (8002番ポート: FastAPI)

5. **「インスタンスを起動」**をクリック
6. SSHで接続してDockerセットアップ

---

## 📞 困ったときの対処法

### Q1. 管理者が誰かわからない
**A**: AWSアクセスポータルのログイン画面に記載されている組織名やドメイン名から問い合わせ先を探す

### Q2. 権限が付与されるまでどれくらいかかる?
**A**: 通常は数分〜数時間。管理者の承認フローによる

### Q3. PowerUserAccessとAdministratorAccessの違いは?
**A**:
- **PowerUserAccess**: ほぼ全権限 (IAMユーザー管理以外)
- **AdministratorAccess**: 完全な全権限
- デプロイには**PowerUserAccess**で十分

### Q4. AWS CLIの設定がうまくいかない
**A**: マネジメントコンソール (ブラウザ) から手動デプロイすることも可能

---

## 📅 タイムライン (想定)

| タイミング | 作業内容 | 所要時間 |
|----------|---------|---------|
| **現在** | 管理者に権限依頼 | - |
| **+数時間〜1日** | 権限付与待ち | - |
| **権限付与後** | AWS CLI設定 | 10分 |
| **+30分** | EC2インスタンス作成 | 30分 |
| **+1時間** | Docker環境構築 | 30分 |
| **+1.5時間** | プロジェクトデプロイ | 30分 |
| **+2時間** | 動作確認完了 | 30分 |

**合計**: 権限付与後、約2時間でデプロイ完了

---

## ✅ 現在やるべきこと

1. **管理者に上記のメッセージを送る** (最優先)
2. **AWSアクセスポータルのURLを確認** (管理者への連絡に必要な場合)
3. **権限付与の通知を待つ**

権限が付与されたら、すぐにデプロイを開始できます！

---

**最終更新**: 2025-10-09
**ステータス**: 管理者からの権限付与待ち
