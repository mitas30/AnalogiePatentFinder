import json,logging,os,shutil,re,datetime
import fitz
from typing import Tuple
from fitz import Document
from openai import OpenAI
from models.model import patentDocument

logger = logging.getLogger(__name__)

class SplitError(Exception):
    """特定の分割操作で期待される条件を満たさない場合に発生する例外"""
    pass

#GPTを使うクラス
class gptClient:
    def __init__(self):
        self.openai_api_key = self.load_api_key()
        self.client=OpenAI(api_key=self.openai_api_key)
        
    def _load_api_key()->str:
        # JSON設定ファイルを開いて読み込む
        with open('../config.json', 'r') as file:
            config = json.load(file)
        return config['OPENAI_API_KEY']
    
    def make_brief_summary(summary:str)->str:
        "要約から、非専門家でもわかりやすい要約を再構成し、これをstringで返却する"
        return ""
    
class pdfDataProcessor:
    """PDFデータを抽出、加工する。"""
    ERROR_IN_ABSTRACT = -1
    ERROR_IN_DETAIL = -2
    ERROR_IN_OTHER = -3

    def __init__(self, fetch_folder_path=None, exception_folder=None):
        if fetch_folder_path is None:
            fetch_folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/patentPDFs/not_processed")
        if exception_folder is None:
            exception_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/patentPDFs/error_file")

        #正規化して形式を統一する
        self.fetch_folder_path = os.path.normpath(fetch_folder_path)
        self.exception_folder = os.path.normpath(exception_folder)
        
    def getExceptionFolder(self, error_code):
        """
        エラーコードに基づき、対応する例外フォルダのパスを返す。

        Parameters:
        error_code (int): 発生したエラーの種類を表すコード。

        Returns:
        str: 対応する例外フォルダのパス。
        """
        if error_code == self.ERROR_IN_ABSTRACT:
            folder_name = "AboutAbstract"
        else:
            folder_name = "Others"
        return os.path.join(self.exception_folder, folder_name)
    
    def convertClassStrToList(self,ipc_class_str)->list[str]:
        """class_strから、単一のキーワードのリストに変換する"""
        class_list=[]
        raw_class_list=re.split("\n",ipc_class_str)
        for raw_keycode in raw_class_list:
            keycode=re.sub("\s+\(.+\)","",raw_keycode)
            class_list.append(keycode)
        return class_list
    
    def _slice_patent_section(self,pdf_document:Document,pattern:str)->str:
        """
        [pattern]より上の部分を切り出して、stringで返す。
        ただし、これが無いものは例外として扱う
        また、patternはraw文字列であることが期待される
        """
        #step1 patternのあるページまで切り出す
        target_page=""
        is_find=False
        for page in pdf_document:
            target_page+=page.get_text("text")
            areas = page.search_for(pattern)
            if areas !=[]:
                is_find=True
                break
        #特許請求の範囲がない場合
        if is_find==False:     
            raise SplitError(f"""特許文書が正式なフォーマットに従っていない。--{pattern}が存在しない""")
        #step2 patternより上の、最初の連続部分文字列を返す
        ret_str=re.split(pattern,target_page)[0]
        return ret_str
        
    def extract_needed_data(self,file_path:str)->tuple:
        """
        1つの公開特許広報から特定の情報を抽出する。
        公表特許公報(グローバルな出願)は、フォーマットが異なるため、使えない。
        Parameters:
        file_path (str): 抽出するファイルのpath

        成功した場合は、(apply_number(p_key,int),invent_name, problem, solve_way,ipc_class_list(list[str]),apply_date(datetime)) のタプルを返す。
        失敗した場合は、SplitErrorを返す
        """
        pdf_doc=fitz.open(file_path)
        #step1: 要約を含んだ、文書の上の部分だけを切り取る(選択図で)
        doc_description=self._slice_patent_section(pdf_doc,r"【選択図】")
        #step2: step1のstringから、情報を抽出する。
        #2-1 要約から上と下で分ける
        split_list=re.split(r"【\s*要\s*約\s*】.*\n",doc_description)
        if len(split_list)!=2:
            raise SplitError("【要約】が存在しない")
        basic_info=split_list[0]
        abstract=re.sub(r"\n","",split_list[1])
        #NOTE【選択図】があるが、要約から離れた位置に存在している場合、または[化*]が存在するときlen(m)!=2
        #NOTE ただし、これらの例外は13/3050
        #NOTE 【が2つのときも、[効果]や[構成]のようなときがあるが、この例外も7/3050
        #NOTE 問題を分解する教師あり分類器の都合上、課題と解決手段が存在している特許だけを受け付ける
        #2-2 要約を課題と手段に分ける 
        split_list=re.split(r"【\w*課題】|【\w*手段】",abstract)
        if(len(split_list)!=3):
            raise SplitError(f"要約が課題と手段に分かれていない split_len={str(len(split_list))}")
        problem=split_list[1]
        solve_way=split_list[2]
        #step3 step1のstringから基本的な特許情報を抽出する
        basic_info_list=re.split("【発明の名称】|Int\.Cl.+\n",basic_info)
        if(len(basic_info_list)!=3):
            logger.log(logging.DEBUG,f"{str(len(split_list))}\nfile_path={file_path}")
        invent_name=re.match(".+",basic_info_list[2]).group()
        #3-1 出願番号を取得する
        if extracted_number:=re.search(r'特願(\d{4})-(\d+)',basic_info_list[1]):
            year = extracted_number.group(1)
            number = int(extracted_number.group(2))
            apply_number = f"{year}{number:06}"
        else:
            raise SplitError("出願番号が存在しない") 
        #3-2 IPC class_listを取得する
        ipc_class_str=re.split("\nＦＩ",basic_info_list[1])[0]
        ipc_class_list=self.convertClassStrToList(ipc_class_str)
        #3-3 出願日を取得する(Date型で格納する)
        if date_list:=re.search(r"\(22\)[^\(]+\((\d+)\.(\d+)\.(\d+)\)\n",basic_info_list[1]):
            apply_date=datetime.datetime(int(date_list.group(1)),int(date_list.group(2)),int(date_list.group(3)))
        else:
            raise SplitError("出願日が存在しない") 
        return apply_number,invent_name, problem, solve_way,ipc_class_list,apply_date
    
    def extract_one_patent(self,file_path:str,patentmanip:patentDocument)->int:
        """ 1つのPDFから情報を取り出す関数。
            結果に応じたコードを返す
        """
        try:
            extract_data=self.extract_needed_data(file_path)
            return patentmanip.add_patent_data(*extract_data)
        except SplitError as e:
            logger.log(logging.WARNING,f"{e}")
            return 1
    
    def _make_flat(self, folder_path: str):
        """
        指定されたフォルダ内のすべてのファイルをフォルダのトップレベルに移動し、
        空になったサブディレクトリを削除する。

        この関数は、指定されたディレクトリ内のファイルをフラットに整理することで、
        ディレクトリ構造を単純化します。同名のファイルが存在する場合、上書きされるリスクがあるため、
        事前に適切なファイル名の管理が必要です。

        Parameters:
            folder_path (str): ファイルをフラットに整理するディレクトリのパス。
        """
        # 指定されたフォルダパス内を再帰的に探索（ボトムアップ）
        for dirpath, dirnames, filenames in os.walk(folder_path, topdown=False):
            for filename in filenames:
                source_path = os.path.join(dirpath, filename)
                destination_path = os.path.join(folder_path, filename)
                # ファイル名の衝突をチェック
                if os.path.exists(destination_path):
                    continue  # 同名ファイルが存在する場合はスキップ
                # ファイルを移動
                shutil.move(source_path, destination_path)
                
            # ディレクトリが空になっているかチェックし、空であれば削除
            if not os.listdir(dirpath) and dirpath != folder_path:
                os.rmdir(dirpath)
    
    def batch_extract_patent_datas(self,folder_path:str):
        """
        指定されたフォルダ(folder_pass)内に存在する全てのPDFファイルから特許データを抽出し、データベースに格納するバッチ処理を行う。
        ただし、サブフォルダに格納されているファイルは取り出す
        抽出やデータベース格納に失敗した場合、ファイルは例外フォルダに移動される。
        """
        logger.log(logging.INFO,"Batch[データベースへの格納] start")
        patentmanip=patentDocument()
        #step1 folder_pathに存在するサブフォルダからも特許fileを取り出す。
        self._make_flat(folder_path)
        error_count=0
        count=0
        #folder_pathで指定されたすべての子孫ファイルに行う
        for filename in os.listdir(folder_path):
            file_path=os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                res_code = self.extract_one_patent(file_path,patentmanip)
                if res_code == 0:
                    os.remove(file_path)
                    count+=1
                else:
                    logger.log(logging.ERROR,f"正常でないpdfファイル:{file_path}")
                    error_count+=1
        logger.log(logging.INFO,f"Batch[データベースへの格納] complete count={count},error_count={error_count}")
    
def provide_brief_summary(application_num: int) -> str:
    """
    特許申請番号に基づいて特許の簡潔な要約を提供する関数。
    まず、GPTによって作成された既存の要約が存在するかどうかをチェックし、存在しない場合はGPTモデルを用いて要約を生成する。

    Args:
    application_num (int): 特許申請の番号。

    Returns:
    str: 特許の簡潔な要約。要約が存在しない場合は空の文字列を返す。
    """
    # 特許文書DBのインスタンスを作成
    patentdoc = patentDocument()

    # 特許申請番号に基づいて簡潔な要約を取得
    brief_summary = patentdoc.get_brief_Summary(application_num)

    # 既に簡潔な要約が存在する場合は、それを返す
    if brief_summary != "":
        return brief_summary

    # GPTクライアントのインスタンスを作成
    gpt = gptClient()

    # 全文の要約を取得
    summary = patentdoc.get_summary()

    # 要約が存在しない場合は、エラーログを出力して空の文字列を返す
    if summary == "":
        logger.error(f"application number {application_num} doesn't have a summary.")
        return ""

    # GPTを使用して簡潔な要約を生成
    brief_summary = gpt.make_brief_summary(summary)

    # 生成した簡潔な要約を特許文書に設定
    patentdoc.set_brief_summary(application_num, brief_summary)

    # 生成した要約を返す
    return brief_summary




