# ベースイメージ
FROM python:3.11

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY requirements.txt ./
RUN pip install -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# アプリケーションの起動(これはdocker runやstartのときに実行される)
CMD ["python", "app.py"]
