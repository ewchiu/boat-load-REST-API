from flask import Blueprint, request, jsonify
from google.cloud import datastore

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix='/loads')

# get all loads/add a load
@bp.route('', methods=['GET', 'POST'])
def loads_get_post():
    
    # add a load
    if request.method == 'POST':
        content = request.get_json()

    if len(content) != 3:
        error = {"Error": "The request object is missing at least one of the required attributes"}
        return jsonify(error), 400

    new_load = datastore.entity.Entity(key=client.key('loads'))
    new_load.update({"volume": content["volume"], 'carrier': {}, 'content': content['content'], 'creation_date': content['creation_date']})
    client.put(new_load)

    new_load['id'] = new_load.key.id
    new_load['self'] = f"{request.url}/{str(new_load.key.id)}"
    return jsonify(new_load), 201