from flask import Blueprint, request, jsonify
from services.api_service import patentInfoProvider, patentUrlFetcher
import logging, json

patents_blueprint = Blueprint("api", __name__)
logger = logging.getLogger(__name__)
# * api層では、サービス層の関数を1つ呼び出して、結果を返すだけ


# * クライアントから検索クエリを受け取って、結果を返すお仕事
@patents_blueprint.route("/search", methods=["GET"])
def search_patents():
    object = request.args.get("problem")
    parameters = json.loads(request.args.get("selected"))
    assert type(object) == str
    assert type(parameters) == list
    logging.log(logging.INFO, f"object={object}\n parameters={parameters}")
    p_provider = patentInfoProvider()
    results = p_provider.fetch_target_patents(object, parameters)
    assert type(results) == list
    apply_nums = "".join(str(result["apply_number"]) + "\n" for result in results)
    logger.log(logging.INFO, f"display_patents:\n{apply_nums}")
    return jsonify(results)


@patents_blueprint.route("/redirect_full_patent", methods=["POST"])
def redirect_full_patent():
    """_summary_
    \n特許庁の特許公報のページにリダイレクトするURLを渡す。
    """
    data = request.json
    apply_number = data.get("apply_number")
    logger.log(logging.INFO, f"apply_number={apply_number} {type(apply_number)}")
    assert type(apply_number) == str
    url_fetcher = patentUrlFetcher()
    redirect_utl = url_fetcher.get_url_to_full_page(apply_number)
    assert type(redirect_utl) == str
    # jsonify({JSONオブジェクト})
    return jsonify({"url": redirect_utl})


@patents_blueprint.route("/make_explain", methods=["POST"])
def make_explain():
    """_summary_

    特許の工夫について、より詳細な説明を生成する。

    詳細な説明から、headingの内容が正確でないことがわかった場合には、headingを改善する処理を挟む。
    """
    data = request.json
    logging.debug("make_explain() " + str(data))
    apply_number = data.get("apply_number")
    heading = data.get("heading")
    key_id = data.get("key_id")
    parameter = data.get("parameter")
    param_exp = data.get("param_exp")
    target_object = data.get("target_object")
    logger.info(f"in meke_explain:{key_id}")
    assert type(apply_number) == str
    assert type(heading) == str
    assert type(param_exp) == str
    assert type(key_id) == str
    p_provider = patentInfoProvider()
    explanation = p_provider.create_and_store_explain(
        apply_number,
        heading,
        key_id,
        param_exp,
        t_object=target_object,
        parameter=parameter,
    )
    struct_exp = p_provider.structure_explanation(
        explanation["patent_explanation"]["output"]
    )
    if explanation["is_heading_improved"] == True:
        return jsonify(
            {
                "is_heading_improved": True,
                "heading": explanation["better_heading"]["output"],
                "abstractSolution": explanation["abstractSolution"]["output"],
                "solution": explanation["solution_summary"]["output"],
                "intro": struct_exp["intro"],
                "strategy": struct_exp["strategy"],
                "application": struct_exp["application"],
            }
        )
    else:
        return jsonify(
            {
                "is_heading_improved": False,
                "intro": struct_exp["intro"],
                "strategy": struct_exp["strategy"],
                "application": struct_exp["application"],
            }
        )


@patents_blueprint.route("/fetch_exist_explanation", methods=["GET"])
def fetch_explanation():
    apply_number = request.args.get("apply_number")
    parameter = request.args.get("parameter")
    p_provider = patentInfoProvider()
    is_exist = p_provider.inquire_explanation(apply_number, parameter)
    if is_exist == False:
        return jsonify({"is_exist": False})
    else:
        struct_exp = p_provider.fetch_exist_explanation(apply_number, parameter)
        return jsonify(
            {
                "is_exist": True,
                "intro": struct_exp["intro"],
                "strategy": struct_exp["strategy"],
                "application": struct_exp["application"],
            }
        )
