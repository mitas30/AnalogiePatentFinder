from flask import Blueprint, request, jsonify
import services.api_service as patent_service

patents_blueprint = Blueprint('api', __name__)

@patents_blueprint.route('/search', methods=['GET'])
def search_patents():
    query = request.args.get('query')
    results = patent_service.search_patents(query)
    return jsonify(list(results))

@patents_blueprint.route('/<id>', methods=['GET'])
def get_patent(id):
    patent = patent_service.get_patent_by_id(id)
    return jsonify(patent)