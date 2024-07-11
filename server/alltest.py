#ここで全てのtestを試す app.pyと同じ設定ですべて動く
from tests.unit_test import model_test as m_test
from setting_log.logging_config import setup_logging
import unittest,logging

setup_logging()

#service_test.st_check_poffice_api(1)
if __name__ == "__main__":
    # 'module' フォルダ内のすべてのテストを見つけて実行します
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests',pattern='*.py')

    runner = unittest.TextTestRunner()
    runner.run(suite)
    
    res=m_test.query_test()
    logging.info(res)