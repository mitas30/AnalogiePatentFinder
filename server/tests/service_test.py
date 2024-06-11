from services.service import pdfDataProcessor,fineTuning,expOperator,patentProcessor
from services import service
import logging
import os

logger = logging.getLogger(__name__)

def test():
    tester=pdfDataProcessor()
    print(tester.fetch_folder_path)
    print(tester.exception_folder)
    
def test_extract_one_patent():
    pdf_processor=pdfDataProcessor()
    # 相対パスをテストスクリプトのディレクトリからの相対パスに変換
    test_file_dir = os.path.dirname(__file__)
    test_file_path = os.path.join(test_file_dir,'../../data/test_data','2023168635.pdf') 
    pdf_processor.extract_one_patent(test_file_path,is_test=True)

#特許PDFフォルダで、複数の特許ファイルを試し、正規表現の妥当性を検証する
def test2():
    tester=pdfDataProcessor()
    #model_tester=pdoc()
    tester.batch_extract_patent_datas(r"D:\PatentData\AnalogieSearch\特許PDF一覧\JPPDFA_20231205\DOCUMENT\P_A1")
    
def st_dismantle_problem(max_doc:int=10):
    """_summary_ \n
        問題を分解する。 max_docで指定されたdoc数だけ行う。
    """
    service.make_span_problems_list(max_doc,is_write=False)
    
def st_uploadfile():
    batch=service.gptBatch()
    batch.upload_batch_file("jsonl_fileplace")
    
def st_makebatch(batch_id:str):
    batch=service.gptBatch()
    batch.make_batch_request(batch_id)
    
def st_checkbatch(batch_id:str):
    batch=service.gptBatch()
    batch.check_batch_status(batch_id)
        
def st_do_fine_tuning():
    finetuner=fineTuning()
    finetuner.do_fine_tuning("function1")
    
def st_analyze_f_tuning(finetune_id:str):
    """"_summary_ fine tuningの結果を分析する
    """
    finetuner=fineTuning()
    finetuner.analyze_fine_tuning_model(finetune_id)
    
def st_annotate_para():
    """_summary_ annotate_improvement_targets_from_patentのテスト
    """
    client=service.gptClient()
    client.annotate_improvement_targets_from_patent([])
    
def st_c_and_s_impr_params(max_doc:int=15):
    """_summary_ create_and_store_improvement_parametersのテスト
    """
    service.create_and_store_improvement_parameters(max_doc,False)
    
def st_batch_dismantle_problem(max_doc:int=10):
    """_summary_\n
    batch処理で問題を分解する。 max_docで指定されたdoc数だけ行う。
    """
    batch=service.gptBatch()
    batch.batch_process("dismantle_problem",max_doc)
    
def st_batch_c_and_s_impr_params(max_doc:int=15):
    """_summary_ batch_create_and_store_improvement_parametersのテスト
    """
    batch=service.gptBatch()
    batch.batch_process("annotate_improvement_parameters",max_doc)
    
#! GPTを使う。parameterの結果を検証するために使用するテスト
def st_check_res_c_and_s_impr_params(id_filename:str, output_filename:str,is_update:bool=False):
    """_summary_ create_and_store_improvement_parametersの結果をlogに表示する\n
    DBに書き込む場合は、writeの方を使う
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "annotate_improvement_parameters",is_update)    

# !GPTを使うし、DBにも書き込むので注意
def st_write_res_c_and_s_impr_params(id_filename:str, output_filename:str,is_update:bool=True):
    """_summary_ create_and_store_improvement_parametersの結果をファイルに書き込む
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "annotate_improvement_parameters",is_update)
    
def st_askbatch(batch_id:str):
    """_summary_ batchの結果を取得する batchが完了していれば、結果を取得する

    Args:
        batch_id (str): _description_
    """
    batch=service.gptBatch()
    batch.ask_batch_result(batch_id)
    
def check_duplicate_patent():
    service.remove_all_documents_with_same_invent_name_and_problem()
    
def aggregate_parameters():
    """ _summary_ 向上パラメータごとの特許数を集計する
    """
    operator=service.expOperator()
    logger.log(logging.INFO,"[向上パラメータ:一致特許数]")
    operator.aggr_clasified_impr_params()
    logger.log(logging.INFO,"\n")
    
def aggregate_function_classes():
    """ _summary_ 抽象的な機能ごとの特許数を集計する
    """
    operator =service.expOperator()
    logger.log(logging.INFO, "[抽象的な機能:一致特許数]")
    operator.aggr_classified_function_classes()
    logger.log(logging.INFO, "\n")
    
def test_uncategorized_function_classes(max_doc: int = 10):
    """未分類のfunction_classesをDBから取得し、処理する
    function_classesの機能が正しく動作しているかを確認するためのテスト
    """
    pp = patentProcessor()
    logger.log(logging.INFO, f"未分類のfunction_classesを持つ特許を{max_doc}件取得")
    pp.categorize_functions(max_doc, is_process=False)
    logger.log(logging.INFO, "\n")

# !GPTを使うし、DBにも書き込むので注意
def categorize_and_write_function_classes(max_doc: int = 50):
    """function_classesを分類し、DBに書き込む
    """
    pp = patentProcessor()
    pp.categorize_functions(max_doc, is_write=True, is_process=True)

#! GPTを使う。class分けの結果を検証するために使用するテスト
def process_function_classes_without_write(max_doc: int = 50):
    """function_classesを処理するが、DBには書き込まない
    """
    pp = patentProcessor()
    pp.categorize_functions(max_doc, is_write=False, is_process=True)
    
def st_check_poffice_api(max_doc:int=1):
    """_summary_ 特許庁APIと正常に通信しているか確認 毎回やってもいいテスト

    Args:
        max_doc (int, optional): _description_. Defaults to 1.
    """
    logger.log(logging.INFO,"[特許庁APIと正常に通信しているか確認]")
    service.update_documents_with_full_url(max_doc=max_doc,is_write=True)
    
# !DBに書き込むので注意すること
def st_fetch_full_url(max_doc:int=100):
    """_summary_
    \nfull_urlの無い特許のURLを特許庁のAPIから取得する。
    \nmax_docで指定されたdoc数だけ行う。
    """
    service.update_documents_with_full_url(max_doc=max_doc,is_write=True)
    
def show_not_headding(max_doc:int=10):
    """_summary_ 未分類の特許を表示する
    """
    pp=patentProcessor()
    logger.log(logging.INFO, f"headdingの無い特許を{max_doc}件取得")
    pp.add_heading(max_doc,is_process=False)
    logger.log(logging.INFO, "\n") 
    
def make_new_abst():
    service.make_new_abstracts()