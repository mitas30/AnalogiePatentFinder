# ベースイメージ
FROM node:16-alpine

# 作業ディレクトリの設定
WORKDIR /app

# 依存関係のインストール
COPY analogical-patent/package*.json ./
RUN npm install

# アプリケーションコードのコピー
COPY analogical-patent .

# 開発サーバの起動(docuer run時)
CMD ["npm", "run", "dev"]