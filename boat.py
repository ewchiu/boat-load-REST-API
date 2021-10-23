from flask import Blueprint, request, jsonify, Response
from google.cloud import datastore

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

# get all/create boats
@bp.route('', methods=['POST', 'GET'])
def boats_post_get():

    # method to create a new boat
    if request.method == 'POST':
        content = request.get_json()

        # check if attributes are missing
        if len(content) != 3:  
            error = {"Error": "The request object is missing at least one of the required attributes"}
            return jsonify(error), 400

        # create new boat in Datastore
        new_boat = datastore.entity.Entity(key=client.key("boats"))
        new_boat.update({"name": content["name"], "type": content["type"],
          "length": content["length"], "loads": []})
        client.put(new_boat)

        # formats response object
        new_boat["id"] = new_boat.key.id
        new_boat["self"] = f"{request.url}/{str(new_boat.key.id)}"

        return jsonify(new_boat), 201

    # method to get all boats
    elif request.method == 'GET':
        query = client.query(kind="boats")
        limit = int(request.args.get('limit', '3'))
        offset = int(request.args.get('offset', '0'))
        iterator = query.fetch(limit=limit, offset=offset)
        pages = iterator.pages
        results = list(next(pages))

        if iterator.next_page_token:
            next_offset = limit + offset
            next_url = f"{request.base_url}?limit={limit}&offset={next_offset}"
        else:
            next_url = None

        for boat in results:
            boat['id'] = boat.key.id
        
        output = {"boats": results}

        if next_url:
            output['next'] = next_url

        return jsonify(output), 200

    else:
        return 'Method not recognized'

# get/delete boat by ID
@bp.route('/<id>', methods=['GET', 'DELETE'])
def boat_id_get_delete(id):

    # get a boat by ID
    if request.method == 'GET':
        boat_key = client.key('boats', int(id))
        boat = client.get(key=boat_key)

        # boat id was not found 
        if not boat:
            error = {"Error": "No boat with this boat_id exists"}
            return jsonify(error), 404

        for load in boat['loads']:
            load['self'] = f"{request.url_root}loads/{str(load['id'])}"

        boat['id'] = id
        boat['self'] = request.url
        return jsonify(boat), 200

    # delete a boat
    elif request.method == 'DELETE':
        boat_key = client.key('boats', int(id))
        boat = client.get(key=boat_key)

        # boat id was not found 
        if not boat:
            error = {"Error": "No boat with this boat_id exists"}
            return jsonify(error), 404

        # remove boat from loads
        if len(boat['loads']) > 0:

            for load in boat['loads']:
                load_key = client.key('loads', load['id'])
                retrieved_load = client.get(key=load_key)
                retrieved_load['carrier'] = None
                client.put(retrieved_load)

        client.delete(boat_key)
        return Response(status=204)

    else:
        return 'Method not recognized'

@bp.route('/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
def add_delete_loads(boat_id, load_id):

    # add load to boat
    if request.method == 'PUT':
        boat_key = client.key('boats', int(boat_id))
        boat = client.get(key=boat_key)
        load_key = client.key("loads", int(load_id))
        load = client.get(key=load_key)

        # boat/load id was not found 
        if not boat or not load:
            error = {"Error": "No boat or load with this id exists"}
            return jsonify(error), 404

        # check if load is already assigned to a boat
        if load['carrier']:
            error = {"Error": "This load already has a boat"}
            return jsonify(error), 403
        
        # check if boat already has this load assigned
        for load in boat['loads']:
            if load['id'] == load.key.id:
                error = {"Error": "This load already has a boat"}
                return jsonify(error), 403

        # add load to boat and vice versa
        load['carrier'] = {'id': boat.key.id, 'name': boat['name']}
        boat['loads'].append({'id': load.key.id})

        client.put(load)
        client.put(boat)
        return Response(status=204)

    # delete load from boat
    elif request.method == 'DELETE':
        boat_key = client.key('boats', int(boat_id))
        boat = client.get(key=boat_key)
        load_key = client.key("loads", int(load_id))
        load = client.get(key=load_key)

        # boat/load id was not found 
        if not boat or not load:
            error = {"Error": "No boat or load with this id exists"}
            return jsonify(error), 404

        # load is not assigned to boat
        if load['carrier'] is None or load['carrier']['id'] != boat.key.id:
            error = {"Error": "The load isn't on this boat"}
            return jsonify(error), 404

        boat['loads'].remove({'id': load.key.id})
        load['carrier'] = None
        client.put(boat)
        client.put(load)
        return Response(status=204)

    else:
        return 'Method not recognized'
        