import json,logging,os,shutil,re,datetime,time
import fitz
from pprint import pprint
from bson.objectid import ObjectId
from typing import Tuple
from fitz import Document
from openai import OpenAI
from models.model import patentDocument 

logger = logging.getLogger(__name__)

class SplitError(Exception):
    """特定の分割操作で期待される条件を満たさない場合に発生する例外"""
    pass

class gptClient:
    '''GPTを使ったメソッド集合のクラス'''
    def __init__(self):
        self.openai_api_key = self._load_api_key()
        self.client=OpenAI(api_key=self.openai_api_key)
        
    def _load_api_key(self)->str:
        # JSON設定ファイルを開いて読み込む
        #ファイルのパスは、実行ファイルからの相対パス
        with open('config.json', 'r') as file:
            config = json.load(file)
        return config['OPENAI_API_KEY']
    
    def upload_file(self,jsonl_filename:str,purpose:str)->str:
        """_summary_  batch処理用のファイルjsonl_filename.jsonlをopenaiにアップロードする

        Args:
            jsonl_fileplace (str): batch処理用のjsonlファイルの名前 場所は必要ない
            例えば、jsonl_fileplace="input"の場合、../data/openai_batch/input/input.jsonlをアップロードする
            purpose: batch処理の目的を指定する(openAI側の引数) batch or fine-tune

        Returns:
            str: file_id(各処理で指定することになるファイルのid)
        """
        file_path="../data"
        if purpose=="batch":
            file_path+="/openai_batch/input/"+jsonl_filename+".jsonl"
        elif purpose=="fine-tune":
            file_path+="/fine-tuning/"+jsonl_filename+".jsonl"
        else:
            logger.log(logging.ERROR,"purposeが不正です")
            return ""
        response = self.client.files.create(
        file=open(file_path, "rb"),
        purpose=purpose
        )
        batchfile_id=response.id
        logger.log(logging.INFO,f"id:{batchfile_id} filesize:{response.bytes}Byte ")
        return batchfile_id
    
    def divide_problems(self,problem_list:list[str],is_collect:bool)->dict[list[str]]:
        ''' summary:\n
            problem_list(10の特許がlistにされている)のproblemは、複数の目的(問題)を述べている可能性がある。\n
            したがって、これを単一のspanに分解する。\n
            is_collectがtrueになっている場合は、会話データを収集する
        '''
        with open('llm_prompt/dismantle.json', 'r', encoding='utf-8') as file:
            #.jsonでは、1つのobjectしか定義できない
            # loadによって、jsonファイルをpythonのデータに変更できる
            data = json.load(file)
        # 特定のキーに対応するデータを取得
        system_message = data.get('system_message')
        user_message = data.get('user')
        example_message = data.get('example')
        model=""
        if is_collect==True:
            model="gpt-4-turbo"
        else:
            #TODO fine-tuningモデルに変更する
            model="ft:gpt-3.5-turbo-0125:personal::9LrSN0B4"
        messages=[
            {"role": "system","content":system_message},
            {"role": "user","content":f"{user_message}\n{example_message}\n<problem>\n{problem_list}"}
        ]
        st=time.time()
        response=self.client.chat.completions.create(model=model,response_format={ "type": "json_object" },messages=messages)
        return_message=json.loads(response.choices[0].message.content)
        logger.log(logging.INFO,f"process_time:{time.time()-st:.2f}s input_token:{response.usage.prompt_tokens} output_token:{response.usage.completion_tokens} model:{response.model}")
        if is_collect==True:
            #jsonl形式に沿うように変換する
            with open('../data/fine-tuning/function1.jsonl',"a",encoding='utf_8') as f:
                insert_json_object={}
                system_obj={"role":"system","content":system_message}
                user_obj={"role":"user","content":f"{user_message}\n{example_message}\n<problem>\n{problem_list}"}
                assistant_obj={"role":"assistant","content":str(return_message)}
                insert_json_object["messages"]=system_obj,user_obj,assistant_obj                
                f.write(json.dumps(insert_json_object,ensure_ascii=False)+'\n')
        return return_message
    
    def make_brief_summary(self,summary:str)->str:
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

class expDataCollector:
    '''実験データの作成に関するクラス'''
    def __init__(self, filename):
        self.filename = filename

    #Legacy: get_all_problems()の廃止
    """def save_problems_to_file(self):
        patent_provider=patentDocument()
        problems = patent_provider.get_all_problems()
        with open(self.filename, 'w', encoding='utf-8') as file:
            for problem in problems:
                file.write(problem + '\n')"""

class gptBatch:
    '''GPTを使ったbatch処理のクラス'''
    def __init__(self):
        self.openai_api_key = self._load_api_key()
        self.client=OpenAI(api_key=self.openai_api_key)
        
    def _load_api_key(self)->str:
        # JSON設定ファイルを開いて読み込む
        #ファイルのパスは、実行ファイルからの相対パス
        with open('config.json', 'r') as file:
            config = json.load(file)
        return config['OPENAI_API_KEY']
        
    def make_batch_request(self,batchfile_id:str)->str:
        """_summary_  batchfile_idを使って、batch処理をopenaiに依頼する

        Args:
            batchfile_id (str): upload_file関数で取得したbatchfile_id
            
        Returns: batch_id: batch処理を識別するためのid
        """
        response = self.client.batches.create(
        completion_window="24h",
        endpoint="/v1/chat/completions",
        input_file_id=batchfile_id
        )
        batch_id=response.id 
        logger.log(logging.INFO,f"batch_id:{batch_id}")
        return batch_id
        
        
    def check_batch_status(self,batch_id:str)->str:
        """_summary_  batch_idを使って、batch処理のstatusを確認する

        Args:
            batch_id (str): make_batch_requestで取得したbatch_id

        Returns:
            str: batch処理のstatus
        """
        response = self.client.batches.retrieve(batch_id)
        logger.log(logging.INFO,f"status:{response.status}")
        return response.status
    
    def get_batch_output_file_id(self,batch_id:str)->str:
        """_summary_ batch_idを使って、batch処理の結果であるjsonlファイルのidを取得する

        Args:
            batch_id (str): 

        Returns:
            str: _description_
        """
        response = self.client.batches.retrieve(batch_id)
        return response.output_file_id
        
    def get_batch_result(self,output_file_id:str)->None:
        """_summary_  batch_idを使って、batch処理の結果であるjsonlファイルを取得する

        Args:
            output_file_id (str): get_batch_output_file_idで取得したoutput_file_id
        """
        jsonl_content = self.client.files.content(output_file_id).text
        with open("../data/openai_batch/res/batch_"+output_file_id+".jsonl", 'w', encoding='utf-8') as file:
            file.write(jsonl_content)
    
    def ask_batch_result(self,batch_id:str)->None:
        """_summary_  batch_idを使って、batch処理の結果を取得する。 batchが完了している場合は、output.jsonlに結果が書き込まれる

        Args:
             (str): get_batch_output_file_idで取得したoutput_file_id
        """
        status=self.check_batch_status(batch_id)
        if status=="completed":
            output_file_id=self.get_batch_output_file_id(batch_id)
            self.get_batch_result(output_file_id)
        else:
            logger.log(logging.INFO,f"status:{status}")
    
    def batch_dismantle_problem(self,max_doc:int=None):
        ''' 
        _summary_ dismantle(文章から目的を取り出す処理)のbatch処理を行う。batchが完了したときに、データ収集まではしてくれない
            
        Args:
            max_doc: 処理するdocの最大数 Noneの場合は、全ての該当docを処理する
        '''
        db_cli=patentDocument()
        #step1 span_problem_listのフィールドを持たないdocumentから情報を取り出す。
        # max_docがNoneの場合は、全てのdocを処理するが、それ以外の場合は、max_docの数だけ処理する
        doc_list=db_cli.get_all_problems_dont_have_span_problem_list(max_doc)
        #step1.5 dismantle.jsonを読み込む
        with open('llm_prompt/dismantle.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        system_message = data.get('system_message')
        user_message = data.get('user')
        example_message = data.get('example')
        #step2 batch処理に使用するinputのjsonlファイルを作成する
        doc_num=len(doc_list)
        problem_list = []
        id_memo=[]
        #NOTE 10個ずつ問題を処理する
        for idx in range((doc_num+9)//10):
            part_doc_list=doc_list[10*idx:min(10*(idx+1),doc_num)]
            id_list=[str(d["id"]) for d in part_doc_list]
            problem_chunk=[d["problem"] for d in part_doc_list]
            problem_list.append(problem_chunk)
            id_memo.append({str(idx):id_list})
        jsonl_data=[]
        for idx,problem_chunk in enumerate(problem_list):
            request = {
                "custom_id": f"request-{idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4-turbo",
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": f"{system_message}"},
                        {"role": "user","content":f"{user_message}\n{example_message}\n<problem>\n{problem_chunk}"}
                    ]
                }
            }
            #json.dumps()は、オブジェクトをシングルラインで書き込むので安心
            jsonl_data.append(json.dumps(request,ensure_ascii=False))
        #step3 jsonlファイルを作成する 
        #ObjectIDのリストを持つmemo,batch処理に使用するinput,問題のリストを持つproblemの3つのファイルを作成する
        with open("../data/openai_batch/memo/"+re.sub(r'\.',r'_',str(time.time()))+".jsonl", 'w', encoding='utf-8') as file:
            for item in id_memo:
                file.write(json.dumps(item)+'\n')
        jsonl_fileplace="in_"+re.sub(r'\.',r'_',str(time.time()))
        jsonl_filepath="../data/openai_batch/input/"+jsonl_fileplace
        with open(jsonl_filepath+".Jsonl", 'w', encoding='utf-8') as file:
            for item in jsonl_data:
                file.write(item + '\n')
        with open("../data/openai_batch/memo/problem_"+re.sub(r'\.',r'_',str(time.time()))+".json", 'w', encoding='utf-8') as file:
            file.write(json.dumps(problem_list,ensure_ascii=False))
        #step4 batch処理をopenaiに依頼する
        gpt_manip=gptClient()
        batchfile_id=gpt_manip.upload_file(jsonl_fileplace,"batch")
        self.make_batch_request(batchfile_id)
 
class fineTuning:
    def __init__(self):
        self.openai_api_key = self._load_api_key()
        self.client=OpenAI(api_key=self.openai_api_key)
    
    def _load_api_key(self)->str:
        # JSON設定ファイルを開いて読み込む
        #ファイルのパスは、実行ファイルからの相対パス
        with open('config.json', 'r') as file:
            config = json.load(file)
        return config['OPENAI_API_KEY']
    
    def make_fine_tuning_request(self,training_file:str)->str:
        """_summary_ fine-tuningのリクエストをopenaiに送信する

        Args:
            training_file (str): fine-tuningのためのjsonlファイルに対応するid

        Returns:
            str: 各fine-tuningに割り当てられたid
        """
        response=self.client.fine_tuning.jobs.create(
            training_file=training_file,
            model="gpt-3.5-turbo",
        )
        response_id=response.id
        return response_id
        
    def do_fine_tuning(self,jsonl_filename:str)->str:
        """_summary_ fine-tuningのリクエストをopenaiに送信する

        Args:
            jsonl_filename (str): fine-tuningのためのjsonlファイルの名前
        
        Returns: fine_tune_id: fine-tuningのid
        """
        gpt_manip=gptClient()
        filename=gpt_manip.upload_file(jsonl_filename,"fine-tune")
        fine_tune_id=self.make_fine_tuning_request(filename)
        logger.log(logging.INFO,f"fine_tune_id:{fine_tune_id}")
        return fine_tune_id
        
    def analyze_fine_tuning_model(self,finetune_id:str)->None:
        """_summary_ fine-tuningの結果を分析する step,train_loss,validation_lossを表示する
        また、検証データを追加していた場合は、その結果(valid_loss,valid_mean_token_accuracy)も表示する

        Args:
            finetune_id (str): 各fine-tuningに割り当てられたid
        """
        job=self.client.fine_tuning.jobs.retrieve(finetune_id)
        result_file_id=job.result_files[0]
        content=self.client.files.content(result_file_id).text
        logger.log(logging.INFO,content)
        
    def evaluate_fine_tuning_model(self,finetune_model_id:str)->None:
        """_summary_ fine-tuningの結果を評価する

        Args:
            finetune_model_id (str): 
        """


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

def make_span_problems_list(max_doc:int=None,
                            is_collect:bool=False,is_write:bool=True):
    """
        summary:\n
        max_doc個のproblemの文章を、複数の目的(問題)のspanのlistに加工する。\n
        一度に10の文章を処理し、bulk_writeによってmongoに一度に書き込む。\n
        is_correct==Trueの場合はfine-tuning用のデータを収集し、is_write==Trueの場合は、DBに書き込む
        
        Args: max_doc: 処理するdocの最大数 Noneの場合は、全ての該当docを処理する
        is_collect: fine-tuning(または、検証)用のデータを作成するかどうか
        is_write: DBに書き込むかどうか
    """
    #step1 span_problem_listの無いdocumentから情報を取り出す。
    db_cli=patentDocument()
    doc_list=db_cli.get_all_problems_dont_have_span_problem_list(max_doc)
    client=gptClient()
    doc_num=len(doc_list)
    #NOTE 10個ずつ処理する    
    for i in range((doc_num+9)//10):
        #step2-1 GPTでspan_problemを取り出す
        part_doc_list=doc_list[10*i:min(10*(i+1),doc_num)]
        id_list=[d["id"] for d in part_doc_list]
        problem_list=[d["problem"] for d in part_doc_list]
        span_p_dict=client.divide_problems(problem_list,is_collect)
        if len(span_p_dict)!=len(part_doc_list):
            logger.log(logging.ERROR,f"""problemの数とoutputの数が合わない
                       {len(part_doc_list)}だけproblemは入っているが、outputは{len(span_p_dict)}""")
            for value in span_p_dict.values():
                print(value)
            continue
        #step2-2 DBにspan_problemを挿入する
        if is_write==True:
            db_cli.bulk_update_span_problem_list(id_list,span_p_dict)
            logger.log(logging.INFO,f"update{i} is done. {len(id_list)} documents are updated.")
        else:
            logger.log(logging.INFO,problem_list)
            logger.log(logging.INFO,'-'*50)
            logger.log(logging.INFO,f"answer:\n{span_p_dict}")
        

# JSONオブジェクトを読み込むための関数
def read_jsonl(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def write_batchf1_result_to_database(problems_fileplace:str,
                                     id_memo_fileplace:str,
                                     output_fileplace:str,
                                     is_collect:bool=False,):
    """_summary_ batch_dismanle_problemの結果をデータベースに書き込む

    Args:
        problems_fileplace (str): batch_dismanle_problemで処理したinputを保管するjsonファイル名
        id_memo_fileplace (str): batch_dismanle_problemで処理したデータのobjectIDを保管するjsonファイル名
        output_fileplace (str): batch_dismanle_problemで処理したoutputを保管するjsonlファイル名
        is_collect (bool): fine-tuning(または、検証)用のデータを作成するかどうか
    """
    input=read_jsonl("../data/openai_batch/memo/"+problems_fileplace+".json")
    id_memo=read_jsonl("../data/openai_batch/memo/"+id_memo_fileplace+".jsonl")
    output=read_jsonl("../data/openai_batch/res/"+output_fileplace+".jsonl")
    db_cli=patentDocument()
    #id_memoとoutputを使って、dbに書き込む
    for (id_chunk,input_chunk,output_chunk) in zip(id_memo,input[0],output):
        str_id_list=id_chunk.values()
        str_result=output_chunk.get("response").get("body").get("choices")[0].get("message").get("content")
        for str_id_val in str_id_list:
            id_list=[ObjectId(str_id) for str_id in str_id_val]
        # 正規表現を用いて [???] 形式のテキストを全て抜き出す
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, str_result)
        span_p_dict={(index+1):match.split(",") for index,match in enumerate(matches)}
        if len(span_p_dict)!=10:
            logger.log(logging.ERROR,f"エラー: {len(span_p_dict)}")
            for keys in id_chunk.keys():
                print(keys)
            pprint(str_result)
            for value in span_p_dict.values():
                print(value)
        else:
            logger.log(logging.INFO,"ok")
            if is_collect==True:
                with open('llm_prompt/dismantle.json', 'r', encoding='utf-8') as file:
                    data=json.load(file)
                system_message = data.get('system_message')
                user_message = data.get('user')
                example_message = data.get('example')
                #jsonl形式に沿うように変換する
                with open('../data/fine-tuning/function1.jsonl',"a",encoding='utf_8') as f:
                    insert_json_object={}
                    system_obj={"role":"system","content":system_message}
                    user_obj={"role":"user","content":f"{user_message}\n{example_message}\n<problem>\n{input_chunk}"}
                    assistant_obj={"role":"assistant","content":str(span_p_dict)}
                    insert_json_object["messages"]=system_obj,user_obj,assistant_obj
                    f.write(json.dumps(insert_json_object,ensure_ascii=False)+'\n')
            #db_cli.bulk_update_span_problem_list(id_list,span_p_dict) 