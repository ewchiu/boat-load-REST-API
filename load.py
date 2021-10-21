from flask import Blueprint, request
from google.cloud import datastore

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix='/loads')