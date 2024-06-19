from services.service import pdfDataProcessor,fineTuning,expOperator,patentProcessor
from services import service
    
# !DBに書き込むので注意すること
def test_fetch_full_url(max_doc:int=100):
    """_summary_
    \nfull_urlの無い特許のURLを特許庁のAPIから取得する。
    \nmax_docで指定されたdoc数だけ行う。
    """
    service.update_documents_with_full_url(max_doc=max_doc,is_write=True)
    
def test_do_fine_tuning():
    finetuner=fineTuning()
    finetuner.do_fine_tuning("function1")
    
def test_analyze_f_tuning(finetune_id:str):
    """"_summary_ fine tuningの結果を分析する
    """
    finetuner=fineTuning()
    finetuner.analyze_fine_tuning_model(finetune_id)
    