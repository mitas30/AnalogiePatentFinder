from flask import Flask
from flask_cors import CORS
from setting_log.logging_config import setup_logging
from api.api import patents_blueprint

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # 任意のオリジンを許可
app.register_blueprint(patents_blueprint, url_prefix='/api')

# ログ設定を初期化
setup_logging()

if __name__ == "__main__":
    app.run(debug=True)