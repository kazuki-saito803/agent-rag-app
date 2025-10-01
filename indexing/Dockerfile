# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 必要なら system パッケージをインストール
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt をコピーして依存をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# FastAPI を uvicorn で起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]