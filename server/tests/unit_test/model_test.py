import unittest
from unittest.mock import MagicMock,patch
from pymongo import UpdateOne
from pymongo.collection import Collection
from bson import ObjectId
from models.model import patentBulkUpdater,DualCollectionConnector,patentQuery

#* ユニットテストは、外部依存関係をモックで置き換える。
#* この狙いは、ローカルで定義した関数やクラスが、意図した振る舞いをするかを確認すること。
#* つまり、dbから、意図したドキュメントを取り出せているか確認したい場合には、統合テストとなる。
#* 統合テストでは、実際のdbや、テスト用のdbを使って、テストを行う。

class testPatentBulkUpdater(unittest.TestCase):

    def setUp(self):
        self.mock_collectionB = MagicMock()

        # Mock the MongoClient and its behavior
        mock_db_client = MagicMock()
        mock_db_client.__getitem__.return_value.__getitem__.return_value = self.mock_collectionB

        # Initialize the patentBulkUpdater with mock parameters
        DualCollectionConnector.__init__ = MagicMock(return_value=None)
        patentBulkUpdater.__init__ = MagicMock(return_value=None)

        self.processor = patentBulkUpdater(collection_name="patents", db_name="analogie_finder")
        self.processor.collectionB = self.mock_collectionB

    def test_bulk_update_heading(self):
        # テスト用のid_list
        id_list = [ObjectId() for _ in range(10)]

        # テスト用の結果データ
        result = {
            'data1': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（測定精度）を向上させる方法を示していないため'},
            'data 2': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（照明強度）を向上させる方法を示していないため'},
            'data  3': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（外的損害に対する耐性）を向上させる方法を示していないため'},
            'data4': {'solution': '0', 'Reason':""},
            'data5': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（適応性または多用途性）を向上させる方法を示していないため'},
            'data6': {'solution': '短い柱材と長い柱材を梁材で溶接固定し、土台に固定して螺旋杭を打ち込む',
                      'Heading': '短い柱と長い柱を梁で固定し、土台に固定して杭を打ち込むことで、架台の安定性を確保する',
                      'abstractSolution': '構造を固定し安定させる'},
            'data7': {'solution': '短い柱材と長い柱材を梁材で溶接固定し、土台に固定して螺旋杭を打ち込む',
                      'heading': '短い柱と長い柱を梁で固定し、土台に固定して杭を打ち込むことで、架台の安定性を確保する',
                      'abstractSolution': '構造を固定し安定させる'},
            'data8': {'solution': 'レーザー光を複数の光ファイバー束で伝送し、加工ヘッドで照射する',
                      'heading': 'レーザー光を複数の光ファイバーで伝え、加工ヘッドから照射する'
                      },
            'data9': {'solution': 'レーザー光を複数の光ファイバー束で伝送し、加工ヘッドで照射する',
                      'heading': 'レーザー光を複数の光ファイバーで伝え、加工ヘッドから照射する',
                      'abstractSolution': '多重伝送を使用して光を分配する'},
            'data 10': {'solution': '検索クエリに基づいて、地理的情報を取得し、不動産物件を抽出する',
                       'heading': '検索クエリと画像データから地理情報を取得し、不動産物件を抽出する',
                       'abstractSolution': '情報を使って対象を特定する'},
        }

        self.processor.bulk_update_heading(id_list, result)

        # 期待される出力結果
        expected_operations = [
            UpdateOne({'_id': id_list[0]}, {'$set': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（測定精度）を向上させる方法を示していないため'}}),
            UpdateOne({'_id': id_list[1]}, {'$set': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（照明強度）を向上させる方法を示していないため'}}),
            UpdateOne({'_id': id_list[2]}, {'$set': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（外的損害に対する耐性）を向上させる方法を示していないため'}}),
            UpdateOne({'_id': id_list[4]}, {'$set': {'solution': '0', 'reason': 'solve_wayはobjectのparameter（適応性または多用途性）を向上させる方法を示していないため'}}),
            UpdateOne({'_id': id_list[6]}, {'$set': {'solution': '短い柱材と長い柱材を梁材で溶接固定し、土台に固定して螺旋杭を打ち込む',
                                                     'heading': '短い柱と長い柱を梁で固定し、土台に固定して杭を打ち込むことで、架台の安定性を確保する',
                                                     'abstractSolution': '構造を固定し安定させる'}}),
            UpdateOne({'_id': id_list[8]}, {'$set': {'solution': 'レーザー光を複数の光ファイバー束で伝送し、加工ヘッドで照射する',
                                                     'heading': 'レーザー光を複数の光ファイバーで伝え、加工ヘッドから照射する',
                                                     'abstractSolution': '多重伝送を使用して光を分配する'}}),
            UpdateOne({'_id': id_list[9]}, {'$set': {'solution': '検索クエリに基づいて、地理的情報を取得し、不動産物件を抽出する',
                                                     'heading': '検索クエリと画像データから地理情報を取得し、不動産物件を抽出する',
                                                     'abstractSolution': '情報を使って対象を特定する'}}),
        ]

        self.mock_collectionB.bulk_write.assert_called_once_with(expected_operations, ordered=False)

def query_test():
    p=patentQuery("patents")
    res=p.find_patents_by_query(abstract_classes=["31","32", "33", "34"],
                            improve_parameters=["27", "28"])
    return res
