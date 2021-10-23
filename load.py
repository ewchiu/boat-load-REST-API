from flask import Blueprint, request, jsonify, Response
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
        new_load.update({"volume": content["volume"], 'carrier': None, 'content': content['content'], 'creation_date': content['creation_date']})
        client.put(new_load)

        new_load['id'] = new_load.key.id
        new_load['self'] = f"{request.url}/{str(new_load.key.id)}"
        return jsonify(new_load), 201

    # get a load
    if request.method == 'GET':
        query = client.query(kind='loads')
        limit = int(request.args.get('limit', '3'))
        offset = int(request.args.get('offset', '0'))
        iterator = query.fetch(limit=limit, offset=offset)
        pages = iterator.pages
        results = list(next(pages))

        if iterator.next_page_token:
            next_offset = offset + limit
            next_url = f"{request.base_url}?limit={limit}&offset={next_offset}"
        else:
            next_url = None

        for load in results:
            load['id'] = load.key.id
        
        output = {"loads": results}

        if next_url:
            output['next'] = next_url

        return jsonify(output), 200

# get/delete load by id
@bp.route('/<id>', methods=['GET', 'DELETE'])
def loads_get_delete(id):

    # get load by id
    if request.method == 'GET':
        load_key = client.key('loads', int(id))
        load = client.get(key=load_key)

        # boat id was not found 
        if not load:
            error = {"Error": "No load with this load_id exists"}
            return jsonify(error), 404

        if load['carrier']:
            load['carrier']['self'] = f"{request.url_root}boats/{str(load['carrier']['id'])}"

        load['id'] = id
        load['self'] = request.url
        return jsonify(load), 200

    # delete load 
    elif request.method == 'DELETE':
        load_key = client.key('loads', int(id))
        load = client.get(key=load_key)

        # boat id was not found 
        if not load:
            error = {"Error": "No load with this load_id exists"}
            return jsonify(error), 404

        if load['carrier']:
            boat_key = client.key('boats', load['carrier']['id'])
            boat = client.get(key=boat_key)
            boat['loads'].remove({'id': load.key.id})
            client.put(boat)

        client.delete(load_key)
        return Response(status=204)

    else:
        return 'Method not recognized'
