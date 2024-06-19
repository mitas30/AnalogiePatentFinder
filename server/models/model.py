from pymongo import MongoClient,UpdateOne
from pymongo.errors import BulkWriteError
from bson.objectid import ObjectId
import json,logging,re

logger = logging.getLogger(__name__)

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
        
class DualCollectionConnector(databaseConnector):
    """
    2つのコレクションを扱う共通機能を提供するクラス。
    """
    def __init__(self, collection_name, collectionB_name="abstracts", db_name="analogie_finder"):
        """
        指定されたデータベースと2つのコレクションを用いてDualCollectionConnectorを初期化します。

        引数:
            collection_name (str): 基本はpatentsコレクション
            collectionB_name (str): 基本はabstractsコレクション
            db_name (str): データベースの名前。デフォルトは 'analogie_finder'。
        """
        super().__init__(collection_name, db_name)  # 親クラスのコンストラクタを呼び出す
        self.collectionB = self.db_client[db_name][collectionB_name]
        
class patentManager(databaseConnector):
    """
    特許データの追加と基本的な取得を担当するクラス。
    特定のIDやキーに基づいたものを担当する
    """
    
    # TODO 0なら成功といいつつ、絶対に0が返るので、なんとかすること
    def add_patent_data(self, patent_data:map) -> int:
        """
        特許データをデータベースに追加します。

        引数:
            apply_number (str): 特許申請番号、主キー
            apply_date (datetime): 申請日
            ipc_class_code_list (list of str): 国際特許分類コードのリスト
            invent_name (str): 発明の名称
            abstract (str): 要約

        戻り値:
            int: 処理結果を示すコード。0なら成功
        """
        apply_number = patent_data['apply_number']
        data = {
            'apply_number': apply_number,
            'invent_name': patent_data['invent_name'],
            'problem': patent_data['problem'],
            'detail_problem': patent_data['detail_problem'],
            'solve_way': patent_data['solve_way'],
            'detail_solve_way': patent_data['detail_solve_way'],
            'ipc_class_code_list': patent_data['ipc_class_code_list'],
            'apply_date': patent_data['apply_date']
        }
        self.collection.update_one(
            {'apply_number': apply_number},
            {'$set': data},
            upsert=True
        )
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
        
    def tmp_func(self,query):
        # full_url属性を持つドキュメントを20個取得
        documents = self.collection.find(
            {"full_url": {"$exists": True}},
            {"problem": 1, "full_url": 1}
        ).limit(20)

        # 結果をリストとして整形して返す
        result = [{"id":str(doc.get("_id")), "title": doc.get("problem"), "url": doc.get("full_url"),"content":" "} for doc in documents]
        return result

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
    
    def get_documents_without_full_url(self, max_doc: int = None) -> list[dict[str, str]]:
        """
        full_urlを持たないすべてのdocumentから、_idとapply_numberを抽出して、listで返すメソッド。

        引数:
            max_doc (int): 取得するdocumentの最大数 (デフォルトはNone)

        戻り値:
            list[dict[str, str]]: _idとapply_numberを持つdocumentのリスト
        """
        query = {'full_url': {'$exists': False}}
        projection = {'_id': 1, 'apply_number': 1}

        if max_doc is None:
            documents = self.collection.find(query, projection)
        else:
            documents = self.collection.find(query, projection).limit(max_doc)

        return [{'id': doc['_id'], 'apply_number': doc['apply_number']} for doc in documents]

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

    def get_documents_without_heading(self, max_doc=None):
        """ _summary_ 
        \nsolutionが存在しないdocumentを取得する。
        \nheadingが存在しないdocumentは、solutionが読み取れないものも含んでいるので、条件としては不適切
        \n$lookupを使って、abstractsコレクションからsolutionを取得しているので、abstractsコレクションのあるdbを指定する必要がある

        Args:
            max_doc (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        pipeline = [
            {
                "$lookup": {
                    "from": "abstracts",
                    "localField": "_id",
                    "foreignField": "original_id",
                    "as": "abstracts"
                }
            },
            {
                "$unwind": "$abstracts"
            },
            {
                "$match": {
                    "abstracts.solution": {"$exists": False},
                    "abstracts.parameter": {"$ne": "0"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "apply_number": 1,
                    "id":"$abstracts._id",
                    "solve_way": 1,
                    "object": 1,
                    "parameter":"$abstracts.parameter",
                    "param_explanation":"$abstracts.parameter_explain"
                }
            }
        ]

        if max_doc is not None:
            pipeline.append({"$limit": max_doc})

        results = self.collection.aggregate(pipeline)
        return list(results)
         
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
    
    def get_function_class_counts(self):
        """
        function_classes(stringのlist)が存在するすべてのdocumentから、function_class(string)を個別に取り出し、
        各stringがそれぞれいくつあるかを[string, count]としたリストとして返す。

        Returns:
            list: 抽象的な機能とその出現回数のリスト。
        """
        pipeline = [
            { "$unwind": "$function_classes" },  # 配列を展開し、各要素を個別のドキュメントとして扱う
            { "$group": { "_id": "$function_classes", "count": { "$sum": 1 } } },  # 各機能ごとにカウント
            { "$addFields": { "fnc_class": {"$toInt":"$_id" }} },  # _idをfnc_classフィールドに追加
            { "$sort": { "fnc_class": 1 } }  
        ]

        results = self.collection.aggregate(pipeline)
        return [[result["fnc_class"], result["count"]] for result in results]

class patentBulkUpdater(DualCollectionConnector):
    """
    特許データの一括更新を担当するクラス。
    """
    #* バッチ処理の結果をDBにいれる関数は、このクラスに置くこと。(id_listとinfo_listを取るように)
    #* これは、config/batch_config.jsonに記載されたupdate_functionを指している
    #* resultは、dict[str,list[dict]]の形式であり、{"識別名":[{結果1},{結果2},...]}の形式に揃える
    def bulk_update_span_problem_list(self, id_list: list[ObjectId], result: dict[str,list[dict]])->int:
        """
        与えられたid_listの数だけ、一気にspan_problem_listを追加する。現在の挙動では、10件ごとに処理することが期待される。
        また、順序なしのbulk操作であるため、エラーを拾うこと。

        引数:
            id_list (list[ObjectId]): 更新対象のドキュメントIDリスト
            info_list (list[dict]): id_listのIDに対応したspan_problem_listを持つdictのリスト
        """
        operations = [
            UpdateOne({'_id': doc_id}, {'$set': {'span_problem_list': result.get('dismantle_problems')[i].get('span_problem_list')}})
            for i, doc_id in enumerate(id_list)
        ]
        try:
            w_cnt=self.collection.bulk_write(operations, ordered=False).modified_count
            return w_cnt
        except BulkWriteError as bwe:
            logger.log(logging.WARNING,bwe.details)
            return 0

    def bulk_update_parameters(self, id_list: list[ObjectId], result: dict[str,list[dict]])->int:
        """
        与えられたid_listの数だけ、一気にinfoを追加する。現在の挙動では、10件ごとに処理することが期待される。
        また、順序なしのbulk操作であるため、エラーを拾うこと。

        引数:
            id_list (list[ObjectId]): 更新対象のドキュメントIDリスト
            info_list (list[dict]): id_listのIDに対応したobjectとparametersを持つdictのリスト
        """
        operations = [
            UpdateOne({'_id': doc_id}, {'$set': {'object': result.get('object_parameters')[i].get('object'), 'parameters': result.get('object_parameters')[i].get('parameters')}})
            for i, doc_id in enumerate(id_list)
        ]
        try:
            w_cnt=self.collection.bulk_write(operations, ordered=False).modified_count
            return w_cnt
        except BulkWriteError as bwe:
            logger.log(logging.WARNING,bwe.details)
            return 0
            
    def bulk_update_function_classes(self, id_list: list[ObjectId], result: dict[str,list[dict]])->int:
        """
        与えられたid_listの数だけ、一気にabstract_functionsを追加する。
        現在の挙動では、50件ごとに処理することが期待される。
        また、順序なしのbulk操作であるため、エラーを拾うこと。

        引数:
            id_list (list[ObjectId]): 更新対象のドキュメントIDリスト
            result (dict): abstract_functionsの結果を持つ辞書
        """
        operations=[]
        i=0
        info_list=result['abstract_functions']
        non_dict_datas=""
        try:
            for info in info_list:
                if isinstance(info, dict):
                    operations.append(UpdateOne(
                        {'_id': id_list[i]},
                        {'$set': {'function_classes': info.get('result')}}
                    ))
                    i+=1
                else:
                    non_dict_datas+=str(info)+" "
        except IndexError as e:
            logger.warning(f"IndexError: {e}")
            return 0
        if non_dict_datas!="":
            logging.warning(f"Skipping non-dict datas : {non_dict_datas}")
        if i!=len(id_list):
            logging.warning(f"Number of id_list and info_list does not match. id_list:{len(id_list)}, info_list:{i}")
            return 0
        try:
            w_cnt=0
            w_cnt=self.collection.bulk_write(operations, ordered=False).modified_count
        except BulkWriteError as bwe:
            logger.log(logging.WARNING,bwe.details)
            w_cnt=0
        return w_cnt
            
    def bulk_update_heading(self, id_list: list[ObjectId], result: dict)->int:
        """_summary_

        Args:
            id_list (list[ObjectId]): _description_
            result (dict): _description_
        
        return: updateに成功したdocumentの数
        """
        operations = []

        # headingsリストを取得
        headings = result.get('headings', [])

        for i, doc_id in enumerate(id_list):
            data_entry = headings[i]
            try:
                update_fields = {'solution': data_entry['solution']}
                if data_entry['solution'] == '0':
                    update_fields['reason'] = data_entry['reason']
                else:
                    update_fields['heading'] = data_entry['heading']
                    update_fields['abstractSolution'] = data_entry['abstractSolution']
                operations.append(UpdateOne({'_id': doc_id}, {'$set': update_fields}))
            except KeyError as key:
                logging.warning(f"Missing key {str(key)} in data entry {data_entry}. Skipping this entry.")

        logger.debug(operations)
        try:
            w_cnt = self.collectionB.bulk_write(operations, ordered=False).modified_count
        except BulkWriteError as bwe:
            logger.log(logging.WARNING, bwe.details)
            w_cnt = 0
        return w_cnt

    def bulk_update_full_url(self, id_list: list[ObjectId], url_list: list[dict])->int:
        """
        与えられたid_listの数だけ、一気にfull_urlを追加する。現在の挙動では、10件ごとに処理することが期待される。
        また、順序なしのbulk操作であるため、エラーを拾うこと。

        引数:
            id_list (list[ObjectId]): 更新対象のドキュメントIDリスト
            url_list (list[dict]): id_listのIDに対応したfull_urlを持つdictのリスト
        """
        operations = [
            UpdateOne({'_id': id_list[i]}, {'$set': {'full_url': url_list[i]['full_url']}})
            for i in range(len(id_list))
        ]
        try:
            w_cnt=self.collection.bulk_write(operations, ordered=False).modified_count
        except BulkWriteError as bwe:
            logger.log(logging.WARNING,bwe.details)
            w_cnt=0
        return w_cnt
        
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

class abstractAdmin(DualCollectionConnector):
    def __init__(self,collection_name):
        super().__init__(collection_name=collection_name)
        self.parameters_explanation = self._load_data()
 
    def _load_data(self):
        with open('other_json_data/improve_parameteres.json', 'r',encoding='utf-8') as file:
            return json.load(file)

    def transfer_parameters(self):
        """
        collectionAからparametersを持つドキュメントを取り出し、collectionBに新しいドキュメントを作成します。
        新しいドキュメントはcollectionAの_idとparameterを持ち、parameter_explainフィールドを追加します。
        処理したドキュメントの数を返します。
        """
        documents = self.collection.find({"parameters": {"$exists": True}, "does_insert_to_abst": {"$ne": True}})
        cnt = 0

        for doc in documents:
            original_id = doc['_id']
            parameters = doc['parameters']
            
            if isinstance(parameters, list):
                for parameter in parameters:
                    explanation = self.parameters_explanation[str(parameter)]
                    new_doc = {
                        "original_id": original_id,
                        "parameter": parameter,
                        "parameter_explain": explanation
                    }
                    self.collectionB.insert_one(new_doc)
            else:
                explanation = self.parameters_explanation[str(parameters)]
                new_doc = {
                    "original_id": original_id,
                    "parameter": parameters,
                    "parameter_explain": explanation
                }
                self.collectionB.insert_one(new_doc)
            
            self.collection.update_one({"_id": original_id}, {"$set": {"does_insert_to_abst": True}})
            cnt += 1
        
        return cnt