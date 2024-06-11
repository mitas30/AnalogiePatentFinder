from flask import Blueprint, request, jsonify
import services.service as service
import logging

patents_blueprint = Blueprint('api', __name__)
logger = logging.getLogger(__name__)
#api層では、サービス層の関数を1つ呼び出して、結果を返すだけ

@patents_blueprint.route('/search', methods=['GET'])
def search_patents():
    query = request.args.get('q')
    results = service.search_patents(query)
    logger.log(logging.INFO, f"search_patents: {results}")
    return jsonify(list(results))