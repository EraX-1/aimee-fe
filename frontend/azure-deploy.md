# Azure へのデプロイ方法

## 主なデプロイオプション

### 1. Azure App Service（推奨）
最も簡単で管理しやすい方法です。

#### 手順：
1. Azure App Service リソースを作成
2. デプロイ方法を選択：
   - GitHub Actions による自動デプロイ
   - Azure CLI を使った手動デプロイ
   - VS Code の Azure 拡張機能を使用

#### Azure CLI でのデプロイ例：
```bash
# リソースグループの作成
az group create --name kenpo-rg --location japaneast

# App Service プランの作成
az appservice plan create --name kenpo-plan --resource-group kenpo-rg --sku B1 --is-linux

# Web アプリの作成
az webapp create --resource-group kenpo-rg --plan kenpo-plan --name kenpo-app --runtime "PYTHON:3.11"

# アプリケーションのデプロイ
az webapp up --resource-group kenpo-rg --name kenpo-app --runtime "PYTHON:3.11"
```

### 2. Azure Container Instances（ACI）
Dockerコンテナとして実行する場合に適しています。

#### 手順：
```bash
# Azure Container Registry の作成
az acr create --resource-group kenpo-rg --name kenpoacr --sku Basic

# Docker イメージのビルドとプッシュ
az acr build --registry kenpoacr --image kenpo-app:v1 .

# コンテナインスタンスの作成
az container create \
  --resource-group kenpo-rg \
  --name kenpo-container \
  --image kenpoacr.azurecr.io/kenpo-app:v1 \
  --dns-name-label kenpo-app \
  --ports 8501
```

### 3. Azure Kubernetes Service（AKS）
大規模なデプロイメントや高可用性が必要な場合。

## Streamlit特有の設定

### config.toml の作成
```toml
[server]
headless = true
port = 8501
enableCORS = false

[browser]
serverAddress = "0.0.0.0"
gatherUsageStats = false
```

### 環境変数の設定
Azure App Service の場合：
```bash
az webapp config appsettings set --name kenpo-app --resource-group kenpo-rg --settings \
  STREAMLIT_SERVER_HEADLESS=true \
  STREAMLIT_SERVER_PORT=8501 \
  STREAMLIT_SERVER_ENABLE_CORS=false
```

## セキュリティ考慮事項

1. **認証の追加**
   - Azure Active Directory 統合
   - App Service の認証機能を有効化

2. **HTTPS の強制**
   ```bash
   az webapp update --name kenpo-app --resource-group kenpo-rg --https-only true
   ```

3. **ネットワークアクセス制限**
   - IP制限の設定
   - Virtual Network 統合

## コスト最適化

1. **App Service プラン**
   - 開発/テスト: B1 (約7,000円/月)
   - 本番環境: S1 以上 (約14,000円/月)

2. **自動スケーリング**
   ```bash
   az monitor autoscale create \
     --resource-group kenpo-rg \
     --resource kenpo-plan \
     --resource-type Microsoft.Web/serverfarms \
     --name kenpo-autoscale \
     --min-count 1 \
     --max-count 3 \
     --count 1
   ```

## GitHub Actions でのCI/CD

`.github/workflows/azure-deploy.yml`:
```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: 'Deploy to Azure Web App'
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'kenpo-app'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

## 監視とログ

1. **Application Insights の有効化**
   ```bash
   az webapp log config --name kenpo-app --resource-group kenpo-rg \
     --application-logging filesystem \
     --web-server-logging filesystem
   ```

2. **メトリクスの確認**
   - CPU使用率
   - メモリ使用率
   - レスポンスタイム

## トラブルシューティング

1. **ポート設定の確認**
   - Streamlit のデフォルトポート 8501 が開いているか確認

2. **起動ログの確認**
   ```bash
   az webapp log tail --name kenpo-app --resource-group kenpo-rg
   ```

3. **環境変数の確認**
   ```bash
   az webapp config appsettings list --name kenpo-app --resource-group kenpo-rg
   ```