#!/bin/sh
set -e

# フラグファイルのパス
FLAG_FILE=/data/db/initialized.flag

# MongoDBをバックグラウンドで起動
mongod --bind_ip_all --logpath /var/log/mongodb.log --fork

# フラグファイルが存在しない場合に初期化処理を実行
if [ ! -f "$FLAG_FILE" ]; then
  echo "First time initialization..."
  # データベースの初期化処理
  mongoimport --host localhost --db analogie_finder --collection patents --type json --file /docker-entrypoint-initdb.d/initial-data.json --jsonArray
  mongoimport --host localhost --db analogie_finder --collection abstracts --type json --file /docker-entrypoint-initdb.d/initial-data2.json --jsonArray
  mongoimport --host localhost --db analogie_finder --collection parameters --type json --file /docker-entrypoint-initdb.d/initial-data3.json --jsonArray

  # フラグファイルを作成
  touch "$FLAG_FILE"
fi

# バックグラウンドで起動したMongoDBをフォアグラウンドに移行
mongod --shutdown

# フォアグラウンドでMongoDBを再起動
exec mongod --bind_ip_all --logpath /var/log/mongodb.log