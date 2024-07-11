import pprint,json,logging,time
import google.generativeai as genai
from setting_log.logging_config import setup_logging

#* 実行ファイルでは、setup_logging()を呼び出す
setup_logging()
logger=logging.getLogger(__name__)

def load_api_info()->dict[str,str]:
    # JSON設定ファイルを開いて読み込む
    #ファイルのパスは、実行ファイルからの相対パス
    with open('config/config.json', 'r') as file:
        config = json.load(file)
    ret_dict={}
    ret_dict["GEMINI_API_KEY"]=config['GEMINI_API_KEY']
    ret_dict["USE_GEMINI_MODEL"]=config['USE_GEMINI_MODEL']
    return ret_dict

if __name__ == "__main__":
    gemini_info = load_api_info()
    assert type(gemini_info)==dict
    genai.configure(api_key=gemini_info["GEMINI_API_KEY"])
    model=genai.GenerativeModel(model_name=gemini_info["USE_GEMINI_MODEL"])
    sentence="2024年7月に、東京都知事選が行われることは知っていますか？\n注目するべき候補について教えて下さい。"
    st=time.time()
    response=model.generate_content(contents=f"{sentence}")
    et=time.time()
    logger.info(f"{round(et-st,4)}s")
    logger.info(response.text)
    logger.info(response.usage_metadata)
    #logger.info(vars(response))