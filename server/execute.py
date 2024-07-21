from services.service import patentProcessor
from services import service
from setting_log.logging_config import setup_logging
import logging
from time import perf_counter

setup_logging()
logger = logging.getLogger(__name__)

def show_not_headding(max_doc:int=10):
    """_summary_ 
    \ncolmn(solution)が存在しないdocumentをmax_doc件取得する
    """
    pp=patentProcessor()
    logger.log(logging.INFO, f"start show_not_headding")
    logger.log(logging.INFO, f"headdingの無い特許を{max_doc}件取得")
    pp.add_heading(max_doc,is_process=True,is_write=False)
    logger.log(logging.INFO, f"complete show_not_headding")

def add_heading(max_doc:int=15):
    """_summary_ headingが存在しない特許にheadingを追加し、DBに書き込む
    """
    pp=patentProcessor()
    logger.log(logging.INFO, f"start add_heading.\nheaddingの無い特許にheadingを追加する")
    pp.add_heading(max_doc,is_process=True,is_write=True)
    logger.log(logging.INFO, f"complete add_heading.")
    
def askbatch(batch_id:str):
    """_summary_ batchの結果を取得する batchが完了していれば、結果を取得する.
    \nbatch_idは、batch処理を頼んだときに表示されているはず。

    Args:
        batch_id (str): _description_
    """
    batch=service.gptBatch()
    batch.ask_batch_result(batch_id)
    
def batch_annotate_parameter(max_doc:int=15):
    batch=service.gptBatch()
    batch.batch_process("annotate_improvement_parameters",max_doc)
    
def batch_categorize_function(max_doc:int=50):
    batch=service.gptBatch()
    batch.batch_process("categorize_functions",max_doc)

def batch_add_heading(max_doc:int=15):
    batch=service.gptBatch()
    batch.batch_process("add_heading",max_doc)
    
#* parameterの結果を検証するために使用する
def check_batch_improve_params(id_filename:str, output_filename:str):
    """_summary_ 
    \nannotate_improvement_parametersの結果をlogに表示する。
    \nDBに書き込む場合は、writeの方を使う。
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "annotate_improvement_parameters",is_write=False)    

def check_batch_categorize_function(id_filename:str, output_filename:str):
    """_summary_ 
    \ncategorize_functionsの結果をlogに表示する。
    \nDBに書き込む場合は、writeの方を使う。
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "categorize_functions",is_write=False)
    
def check_batch_add_heading(id_filename:str, output_filename:str):
    """_summary_ 
    \nadd_headingの結果をlogに表示する。
    \nDBに書き込む場合は、writeの方を使う。
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "add_heading",is_write=False)

#! DBに書き込むので注意すること
def write_batch_improve_params(id_filename:str, output_filename:str):
    """_summary_ 
    \nannotate_improvement_parametersの結果をファイルに書き込む。
    
    Args: 
    \n id_filename: inputフォルダに入っているであろうファイル名 拡張子は必要ない
    \n output_filename: resフォルダに入っているであろうファイル名 拡張子は必要ない
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "annotate_improvement_parameters",is_write=True)
    
def write_batch_categorize_function(id_filename:str, output_filename:str):
    """_summary_ 
    \ncategorize_functionsの結果をファイルに書き込む。
    
    Args: 
    \n id_filename: inputフォルダに入っているであろうファイル名 拡張子は必要ない
    \n output_filename: resフォルダに入っているであろうファイル名 拡張子は必要ない
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "categorize_functions",is_write=True)
    
def write_batch_add_heading(id_filename:str, output_filename:str):
    """_summary_ 
    \nadd_headingの結果をファイルに書き込む。
    
    Args: 
    \n id_filename: inputフォルダに入っているであろうファイル名 拡張子は必要ない
    \n output_filename: resフォルダに入っているであろうファイル名 拡張子は必要ない
    """
    batch=service.gptBatch()
    batch.write_batch_result_to_database(id_filename,output_filename,
                                         "add_heading",is_write=True)
    
def aggregate_parameters():
    """ _summary_ 向上パラメータごとの特許数を集計する
    """
    st_time=perf_counter()
    operator=service.expOperator()
    operator.aggr_clasified_impr_params()
    end_time=perf_counter()
    logger.log(logging.INFO,f"aggregate_parameters:{end_time-st_time}sec.")
    
def aggreate_functions():
    """ _summary_ 機能ごとの特許数を集計する
    """
    operator=service.expOperator()
    operator.aggr_classified_function_classes()
    
def make_new_abstract_documents():
    """_summary_
    \n collection(patents)に存在する特許を使って新しいabstractのデータを作成する関数。
    """
    service.make_new_abstracts()
    
if __name__ == "__main__":
    #aggregate_parameters()
    #aggreate_functions()
    #batch_categorize_function(1000)
    #batch_add_heading(150)
    #askbatch("batch_4OaIVjD1TQ5Mp3J5H12pOBuJ")
    #check_batch_add_heading(id_filename="add_heading_oid_1719042504",output_filename="batch_n8pWi")
    #write_batch_add_heading(id_filename="add_heading_oid_1719042504",output_filename="batch_n8pWi")
    #check_batch_categorize_function(id_filename="categorize_oid_1718797976",output_filename="batch_JHjp3")
    #write_batch_categorize_function(id_filename="categorize_oid_1718797976",output_filename="batch_JHjp3")
    aggregate_parameters()
    aggreate_functions()
    