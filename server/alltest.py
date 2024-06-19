#ここで全てのtestを試す app.pyと同じ設定ですべて動く
from server.tests.unit_test import service_test
from setting_log.logging_config import setup_logging
import unittest

setup_logging()

#service_test.st_check_poffice_api(1)
if __name__ == "__main__":
    # 'module' フォルダ内のすべてのテストを見つけて実行します
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir='tests',pattern='*.py')

    runner = unittest.TextTestRunner()
    runner.run(suite)
    """
    service_test.check_duplicate_patent()
    service_test.test_format_patent_datas()
    service_test.show_not_headding(15)
    """