from services.service import pdfDataProcessor as pdp

#生データをデータベースに入れるバッチ処理
pdf_processor=pdp()
pdf_processor.batchExtractPatentDatas()