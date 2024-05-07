from services.service import pdfDataProcessor ,expDataCollector,fineTuning
from services import service
from models.model import patentDocument as pdoc

def test():
    tester=pdfDataProcessor()
    print(tester.fetch_folder_path)
    print(tester.exception_folder)

#特許PDFフォルダで、複数の特許ファイルを試し、正規表現の妥当性を検証する
def test2():
    tester=pdfDataProcessor()
    #model_tester=pdoc()
    tester.batch_extract_patent_datas(r"D:\PatentData\AnalogieSearch\特許PDF一覧\JPPDFA_20231205\DOCUMENT\P_A1")

def make_exp_data():
    """実験データの作成"""
    tester=expDataCollector('problems.txt')
    tester.save_problems_to_file()
    
def s_test_dismantle_problem(max_doc:int=10):
    """_summary_ \n
        問題を分解する。 max_docで指定されたdoc数だけ行う。
    """
    service.make_span_problems_list(max_doc,is_write=False)
    
def s_test_batch_dismantle_problem(max_doc:int=10):
    """_summary_\n
    batch処理で問題を分解する。 max_docで指定されたdoc数だけ行う。
    """
    batch=service.gptBatch()
    batch.batch_dismantle_problem(max_doc)
    
def s_test_uploadfile():
    batch=service.gptBatch()
    batch.upload_batch_file("jsonl_fileplace")
    
def s_test_makebatch(batch_id:str):
    batch=service.gptBatch()
    batch.make_batch_request(batch_id)
    
def s_test_checkbatch(batch_id:str):
    batch=service.gptBatch()
    batch.check_batch_status(batch_id)
    
def s_test_askbatch(batch_id:str):
    """_summary_ batchの結果を取得する batchが完了していれば、結果を取得する

    Args:
        batch_id (str): _description_
    """
    batch=service.gptBatch()
    batch.ask_batch_result(batch_id)
    
def s_test_batch_span_problem_list():
    service.batch_make_span_problems_list(
        "problem_1714566091_054044",
        "20240501_1615",
        "batch_file-aZCssILcQ9vRBZ0OjacULNDY",
        is_collect=True
        )
    
def s_test_do_fine_tuning():
    finetuner=fineTuning()
    finetuner.do_fine_tuning("function1")
    
def s_test_analyze_f_tuning(finetune_id:str):
    """"_summary_ fine tuningの結果を分析する
    """
    finetuner=fineTuning()
    finetuner.analyze_fine_tuning_model(finetune_id)