from db.dbset import MongoDBClient
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId
from datetime import datetime
from pprint import pprint
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
    
    def get_all_problems_dont_have_span_problem_list(self,max_doc:int)->list[dict[str,str]]:
        '''span_problem_listを持たないすべてのdocumentから、_idとproblemを抽出して、listで返すメソッド'''
        #find({条件}、{select})->cursor(db用イテレータ)
        if max_doc is None:
            problems = self.collection.find(
                {'span_problem_list':{'$exists':False}}, 
                {'_id': 1,'problem': 1}) 
        #doc数が制限されているとき
        else:
            problems = self.collection.find(
                {'span_problem_list':{'$exists':False}},
                {'_id': 1,'problem': 1}).limit(max_doc) 
        # cursorからlistを作成する。
        doc_list=[]
        for doc in problems:
            doc_dict={'id':doc['_id'],
                      'problem':doc['problem']}
            doc_list.append(doc_dict)
        return doc_list
    
    def bulk_update_span_problem_list(self,id_list:list[ObjectId],span_p_dict:dict[list[str]]):
        """_summary_ 与えられたid_listの数だけ、一気にspan_problem_listを追加する。現在の挙動では、10件ごとに処理することが期待される。
            また、順序なしのbulk操作であるため、エラーを拾うこと。
            
        Args:
            id_list (list[ObjectId]): _description_
            span_p_dict (dict[list[str]]): key:list[str]の形で10要素が入っているdict
        """
        operations=[]
        i=0
        for span_problem_list in span_p_dict.values():
            operations.append(UpdateOne({'_id': id_list[i]}, {'$set': {'span_problem_list': span_problem_list}}))
            i+=1
        try:
            self.collection.bulk_write(operations,ordered=False)
        except BulkWriteError as bwe:
            pprint(bwe.details)