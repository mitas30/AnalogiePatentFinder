# ベースイメージ
FROM mongo:latest

# 初期データのコピー
COPY initial-data.json /docker-entrypoint-initdb.d/initial-data.json
COPY initial-data2.json /docker-entrypoint-initdb.d/initial-data2.json
COPY initial-data3.json /docker-entrypoint-initdb.d/initial-data3.json

# エントリーポイントスクリプトのコピー
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# エントリーポイントの設定
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]