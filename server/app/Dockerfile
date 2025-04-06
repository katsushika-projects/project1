FROM python:3.11-slim-bullseye

# PostgreSQL, Firebase SDKに必要なビルドツール
RUN apt-get update && apt-get install -y \
	libpq-dev \
	gcc \
	git \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

# pipアップグレード
RUN pip install --upgrade pip

# Python環境設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 作業ディレクトリ
WORKDIR /app

# パッケージインストール
COPY requirements.txt ./
RUN pip install -r requirements.txt

# アプリ全体コピー
COPY . /app/

# Cloud Run デフォルトポート
ENV PORT=8080

# Firebase用（Cloud Secret Managerと一致させる）
ENV GOOGLE_APPLICATION_CREDENTIALS="/secrets/firebase_key.json"

# 本番用起動コマンド（Gunicorn）
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]
