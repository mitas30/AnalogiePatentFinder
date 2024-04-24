from flask import Flask
from setting_log.logging_config import setup_logging

app = Flask(__name__)

# ログ設定を初期化
setup_logging()

if __name__ == "__main__":
    app.run(debug=True)