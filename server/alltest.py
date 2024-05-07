#ここで全てのtestを試す app.pyと同じ設定ですべて動く
from tests import service_test,model_test
from setting_log.logging_config import setup_logging

setup_logging()
#service_test.make_exp_data()
service_test.s_test_dismantle_problem(max_doc=100)
#service_test.s_test_batch_dismantle_problem(max_doc=100)
#service_test.s_test_askbatch("batch_Q402pRiglrkuFuJlxazXxkPw")
#service_test.s_test_uploadfile()
#service_test.s_test_makebatch("file-8at2bATRWx8wWZcfYl4gIfXZ")
#service_test.s_test_checkbatch("batch_MD9hDoKfGcDzWEzggdzVvNfg")
#service_test.s_test_batch_span_problem_list()
#service_test.s_test_do_fine_tuning()
#service_test.s_test_analyze_f_tuning("ftjob-nxZKk4v5XECKO4K4kJJczpeZ")