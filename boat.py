from flask import Blueprint, request
from google.cloud import datastore

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')