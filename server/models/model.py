from db.dbset import MongoDBClient
from datetime import datetime
#特許文書を操作するクラス
class patentDocument:
    """
    MongoDBの特許コレクションとのやりとりを行うクラスです。

    属性:
        db_client (MongoDBClient): MongoDBとのやりとりに使用するデータベースクライアント。
        collection: MongoDBのコレクションオブジェクト。
    """
    def __init__(self, db_name="analogie_finder", collection_name="patents"):
        """
        指定されたデータベースとコレクションを用いてPatentDocumentを初期化します。

        引数:
            db_name (str): データベースの名前。デフォルトは 'analogie_finder'。
            collection_name (str): コレクションの名前。デフォルトは 'patents'。
        """
        self.db_client = MongoDBClient()
        self.collection = self.db_client.get_collection(db_name, collection_name)

    def add_patent_data(self, apply_number:str,invent_name:str,problem:str,solve_way:str,ipc_class_code_list:list[str],apply_date:datetime)->int:
        """
        特許データをデータベースに追加します。既に存在するapply_numberがある場合は、追加せずに通知します。

        Args:
        apply_number (str): 特許申請番号、主キー
        apply_date (datetime): 申請日
        ipc_class_code_list (list of str): 国際特許分類コードのリスト
        invent_name (str): 発明の名称
        abstract (str): 要約
        """
        # 既に同じ申請番号のデータが存在するか確認
        if self.collection.find_one({'apply_number': apply_number}):
            return 2

        # 新しい特許データを作成
        patent_data = {
            'apply_number': apply_number,
            'invent_name': invent_name,
            'problem':problem,
            'solve_way':solve_way,
            'ipc_class_code_list': ipc_class_code_list,
            'apply_date': apply_date,
        }
        # データベースにデータを追加
        self.collection.insert_one(patent_data)
        return 0
    
    def get_brief_Summary(self, appli_num:int)->str:
        """一度GPTで噛み砕かれていた場合には、データをmongoDBからキャッシュする"""
        document = self.collection.find_one({"appli_num": appli_num})
        if document and "brief_num" in document:
            return document["brief_summary"]
        else:
            return ""  # 空文字を返す
        
    def get_summary(self,appli_num:int)->str:
        """
        出願番号に基づいて特許文書の要約を取得します。

        引数:
            appli_num (int): 特許の出願番号。

        戻り値:
            str: 特許文書の要約。要約が存在しない場合は空文字列を返します。
        """
        document = self.collection.find_one({"appli_num": appli_num})
        if document and "summary" in document:
            return document["summary"]
        else:
            return ""  # 要約がない場合は空文字列を返す
        
    def set_brief_summary(self,application_num:int,brief_summary:str):
        pass