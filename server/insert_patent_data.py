from services.service import pdfDataProcessor as pdp
import os
from setting_log.logging_config import setup_logging

setup_logging()
#生データをデータベースに入れるバッチ処理
current_dir = os.path.dirname(__file__)
test_folder_path = os.path.join(current_dir,'../data/patent_data/P_A1') 
processed_folder_path = os.path.join(current_dir,'../data/patent_data/processed')
pdf_processor=pdp(test_folder_path,processed_folder_path)
pdf_processor.batch_extract_patent_datas(is_test=False)