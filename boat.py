from flask import Blueprint, request, jsonify
from google.cloud import datastore

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

# get/create boats
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