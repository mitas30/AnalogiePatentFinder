#ここで全てのtestを試す app.pyと同じ設定ですべて動く
from tests import service_test
from setting_log.logging_config import setup_logging

setup_logging()
service_test.test2()