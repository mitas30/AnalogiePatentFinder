from pymongo import MongoClient,UpdateOne
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId
from datetime import datetime
from pprint import pprint

#* 複数回のCRUD操作には、pipelineを使用し、複数の挿入操作にはbulk処理を使用すること

class databaseConnector:
    """
    MongoDBのデータベースとコレクションに接続するためのスーパークラス。
    このプロジェクトで使用されるすべてのデータベースコネクタは、このクラスを継承することが想定される。
    """
    def __init__(self, collection_name,db_name="analogie_finder"):
        """
        指定されたデータベースとコレクションを用いてdatabaseConnectorを初期化します。

        引数:
            db_name (str): データベースの名前。デフォルトは 'analogie_finder'。
            collection_name (str): コレクションの名前。
        """
        self.db_client = MongoClient()
        self.collection = self.db_client[db_name][collection_name]
        
class patentManager(databaseConnector):
    """
    特許データの追加と基本的な取得を担当するクラス。
    特定のIDやキーに基づいたものを担当する
    """
    def add_patent_data(self, apply_number: str, invent_name: str, problem: str, solve_way: str, ipc_class_code_list: list[str], apply_date: datetime) -> int:
        """
        特許データをデータベースに追加します。既に存在するapply_numberがある場合は、追加せずに通知します。

        引数:
            apply_number (str): 特許申請番号、主キー
            apply_date (datetime): 申請日
            ipc_class_code_list (list of str): 国際特許分類コードのリスト
            invent_name (str): 発明の名称
            abstract (str): 要約

        戻り値:
            int: 処理結果を示すコード。既に存在する場合は2、新規追加の場合は0。
        """
        if self.collection.find_one({'apply_number': apply_number}):
            return 2

        patent_data = {
            'apply_number': apply_number,
            'invent_name': invent_name,
            'problem': problem,
            'solve_way': solve_way,
            'ipc_class_code_list': ipc_class_code_list,
            'apply_date': apply_date,
        }
        self.collection.insert_one(patent_data)
        return 0
    
    def get_summary(self, appli_num: str) -> str:
        """
        出願番号に基づいて特許文書の要約を取得します。

        引数:
            appli_num (str): 特許の出願番号。

        戻り値:
            str: 特許文書の要約。要約が存在しない場合は空文字列を返します。
        """
        document = self.collection.find_one({"appli_num": appli_num})
        if document and "summary" in document:
            return document["summary"]
        else:
            return ""  # 要約がない場合は空文字列を返す

    def get_brief_summary(self, appli_num: str) -> str:
        """
        要約をGPTでさらに簡単にしたものを取得する。
        つまり、一度GPTで処理されている場合は、mongoDBからキャッシュする

        引数:
            appli_num (str): 特許の出願番号。

        戻り値:
            str: 特許文書の要約。要約が存在しない場合は空文字列を返します。
        """
        document = self.collection.find_one({"appli_num": appli_num})
        if document and "brief_summary" in document:
            return document["brief_summary"]
        else:
            return ""  # 空文字を返す

    def set_brief_summary(application_number: str, brief_summary: str):
        pass
        
class patentQuery(databaseConnector):
    """
    特許データのクエリ操作を担当するクラス。
    フィルタリングや、特定の条件に基づいた検索などは彼が担当する。
    """
    #* バッチ処理ファイル作成のためにDBから特定のデータを取り出す関数は、すべて同じ引数の形に保ち、このクラスに置くこと。(max_docのみを取る)
    #* これは、config/process_config.jsonに記載されたget_documents_funcを指している
    #* 現在なら、~dont_have_span_problem_listと~without_parametersの2つ
    def get_all_problems_dont_have_span_problem_list(self, max_doc: int) -> list[dict[str, str]]:
        """
        span_problem_listを持たないすべてのdocumentから、_idとproblemを抽出して、listで返すメソッド。

        引数:
            max_doc (int): 取得するdocumentの最大数

        戻り値:
            list[dict[str, str]]: _idとproblemを持つdocumentのリスト
        """
        if max_doc is None:
            problems = self.collection.find(
                {'span_problem_list': {'$exists': False}},
                {'_id': 1, 'problem': 1}
            )
        else:
            problems = self.collection.find(
                {'span_problem_list': {'$exists': False}},
                {'_id': 1, 'problem': 1}
            ).limit(max_doc)

        return [{'id': doc['_id'], 'problem': doc['problem']} for doc in problems]

    def get_documents_without_parameters(self, max_doc: int) -> list[dict[str, str, str]]:
        """
        parametersを持たないdocumentから、_idとinvent_nameとproblemを取得して、リストで返すメソッド。

        引数:
            max_doc (int): 取得するdocumentの最大数

        戻り値:
            list[dict[str, str, str]]: _idとinvent_nameとproblemを持つdocumentのリスト
        """
        if max_doc is None:
            documents = self.collection.find(
                {"parameters": {"$exists": False}},
                {"_id": 1, "invent_name": 1, "problem": 1}
            )
        else:
            documents = self.collection.find(
                {"parameters": {"$exists": False}},
                {"_id": 1, "invent_name": 1, "problem": 1}
            ).limit(max_doc)

        return [{"id": doc["_id"], "invent_name": doc["invent_name"], "problem": doc["problem"]} for doc in documents]
    
    def get_documents_without_function_classes(self, max_doc: int = None) -> list[dict[str, str]]:
        """
        属性objectがあり、属性function_classesが存在しないドキュメントから_idとobjectを取得して、リストで返すメソッド。
    
        引数:
            max_doc (int, optional): 取得するドキュメントの最大数。デフォルトはNoneで、すべての該当するドキュメントを取得。
    
        戻り値:
            list[dict[str, str]]: _idとobjectを持つドキュメントのリスト。
        """
        query = {
            "object": {"$exists": True},
            "function_classes": {"$exists": False}
        }
        projection = {"_id": 1, "object": 1}
        
        if max_doc is None:
            documents = self.collection.find(query, projection)
        else:
            documents = self.collection.find(query, projection).limit(max_doc)
        
        return [{"id": doc["_id"], "object": doc["object"]} for doc in documents]    

    def get_parameter_counts(self):
        """
        parameters(stringのlist)が存在するすべてのdocumentから、parameter(string)を個別に取り出し、
        各stringがそれぞれいくつあるかを[string, count]としたリストとして返す。

        Returns:
            list: パラメータとその出現回数のリスト。
        """
        pipeline = [
            { "$unwind": "$parameters" },  # 配列を展開し、各要素を個別のドキュメントとして扱う
            { "$group": { "_id": "$parameters", "count": { "$sum": 1 } } },  # 各パラメータごとにカウント
            { "$addFields": { "para_num": { "$toInt": "$_id" } } },  # _idをint型に変換してpara_numフィールドを追加
            { "$sort": { "para_num": 1 } }
        ]

        results = self.collection.aggregate(pipeline)
        return [[result["para_num"], result["count"]] for result in results]

class patentBulkUpdater(databaseConnector):
    """
    特許データの一括更新を担当するクラス。
    """
    #* バッチ処理の結果をDBにいれる関数は、このクラスに置くこと。(id_listとinfo_listを取るように)
    #* これは、config/batch_config.jsonに記載されたupdate_functionを指している
    #* 現在なら、~span_problem_listと~update_parametersの2つ
    def bulk_update_span_problem_list(self, id_list: list[ObjectId], info_list: list[dict]):
        """
        与えられたid_listの数だけ、一気にspan_problem_listを追加する。現在の挙動では、10件ごとに処理することが期待される。
        また、順序なしのbulk操作であるため、エラーを拾うこと。

        引数:
            id_list (list[ObjectId]): 更新対象のドキュメントIDリスト
            info_list (list[dict]): id_listのIDに対応したspan_problem_listを持つdictのリスト
        """
        operations = [
            UpdateOne({'_id': id_list[i]}, {'$set': {'span_problem_list': document_info['span_problem_list']}})
            for i, document_info in enumerate(info_list)
        ]
        try:
            self.collection.bulk_write(operations, ordered=False)
        except BulkWriteError as bwe:
            pprint(bwe.details)

    def bulk_update_parameters(self, id_list: list[ObjectId], info_list: list[dict]):
        """
        与えられたid_listの数だけ、一気にinfoを追加する。現在の挙動では、10件ごとに処理することが期待される。
        また、順序なしのbulk操作であるため、エラーを拾うこと。

        引数:
            id_list (list[ObjectId]): 更新対象のドキュメントIDリスト
            info_list (list[dict]): id_listのIDに対応したobjectとparametersを持つdictのリスト
        """
        operations = [
            UpdateOne({'_id': id_list[i]}, {'$set': {'object': document_info['object'], 'parameters': document_info['parameters']}})
            for i, document_info in enumerate(info_list)
        ]
        try:
            self.collection.bulk_write(operations, ordered=False)
        except BulkWriteError as bwe:
            pprint(bwe.details)

class patentCleaner(databaseConnector):
    """
    特許データの削除に関連する仕事を行うクラスです。
    """         
    def get_duplicate_ids(self):
        """
        invent_nameとproblemが一致するドキュメントのうち、
        apply_numberが最初のもの以外のIDを取得します。

        戻り値:
            list[ObjectId]: 重複するドキュメントのIDリスト。
        """
        pipeline = [
            {
                "$group": {
                    "_id": {"invent_name": "$invent_name", "problem": "$problem"},
                    "first_id": {"$first": "$_id"},
                    "ids": {"$push": "$_id"}
                }
            },
            {
                "$project": {
                    "ids": {
                        "$filter": {
                            "input": "$ids",
                            "as": "id",
                            "cond": {"$ne": ["$$id", "$first_id"]}
                        }
                    }
                }
            }
        ]

        duplicate_ids = []
        duplicates = self.collection.aggregate(pipeline)
        for duplicate in duplicates:
            if duplicate['ids']:
                duplicate_ids.extend(duplicate['ids'])
        
        return duplicate_ids
    
    def delete_documents_by_ids(self, ids):
        """
        指定されたIDのドキュメントを削除します。

        引数:
            ids (list[ObjectId]): 削除するドキュメントのIDリスト。
        """
        if ids:
            self.collection.delete_many({"_id": {"$in": ids}})
