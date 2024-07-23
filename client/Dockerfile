# ベースイメージ
FROM node:20

# 作業ディレクトリの設定
WORKDIR /app

# RUN COPYは、ビルド時に実行される
#WORKDIRは、以下のコマンドが実行されるディレクトリを指定する
# ちなみに、Bind mountでは、ホストのファイルがそのままコンテナにマウントされるので、COPYは不要

# package.jsonをコピー
COPY analogical-patent/package.json .

# 依存関係のインストール
RUN npm install

# アプリケーションコードのコピー
COPY analogical-patent/ .

# 開発サーバの起動(docuer run時)
# ただし、コマンドで上書きできる
CMD ["npm", "run", "dev"]
