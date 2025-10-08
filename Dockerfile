FROM python:3.11-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY frontend /app/frontend

# 作業ディレクトリをfrontendに設定
WORKDIR /app/frontend

# Streamlitポート公開
EXPOSE 8501

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Streamlit起動
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
