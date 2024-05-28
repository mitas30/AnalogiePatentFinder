#ここで全てのtestを試す app.pyと同じ設定ですべて動く
from tests import service_test
from setting_log.logging_config import setup_logging

setup_logging()
service_test.check_duplicate_patent()
service_test.aggregate_parameters()
service_test.stdb_categorize_function_classes(10)
service_test.st_categorize_function_classes(50)
#service_test.tmp()
#service_test.make_exp_data()
#service_test.st_dismantle_problem(max_doc=100)
#service_test.st_askbatch("batch_Q402pRiglrkuFuJlxazXxkPw")
#service_test.st_uploadfile()
#service_test.st_makebatch("file-8at2bATRWx8wWZcfYl4gIfXZ")
#service_test.st_checkbatch("batch_MD9hDoKfGcDzWEzggdzVvNfg")
#service_test.st_batch_span_problem_list()
#service_test.st_do_fine_tuning()
#service_test.st_analyze_f_tuning("ftjob-nxZKk4v5XECKO4K4kJJczpeZ")
#service_test.st_annotate_para()
#service_test.st_c_and_s_impr_params()
#service_test.st_batch_dismantle_problem(max_doc=30)
#service_test.st_batch_c_and_s_impr_params(max_doc=300)
#service_test.st_askbatch("batch_bBbaRdIuKTOg7I1IR9og6evd")
'''
service_test.st_write_res_c_and_s_impr_params(
    "annotate_memo_1716303841_0195944",
    "batch_23qjN",
)
'''
