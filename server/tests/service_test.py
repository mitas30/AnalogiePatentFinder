from services.service import pdfDataProcessor
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
