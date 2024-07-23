from flask import Flask
from setting_log.logging_config import setup_logging
from api.api import patents_blueprint

app = Flask(__name__)
# /apiであるようなURLリクエストでは、すべてのオリジンを許可する
app.register_blueprint(patents_blueprint, url_prefix='/api')

# ログ設定を初期化
setup_logging()

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)