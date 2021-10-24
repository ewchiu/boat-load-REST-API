from google.cloud import datastore
from flask import Flask, request
import boat
import load

# REST API by Eric Chiu
# Simulates a port with boats that carry loads

app = Flask(__name__)
app.register_blueprint(boat.bp)
app.register_blueprint(load.bp)

@app.route('/')
def index():
    return "Please navigate to /boats to use this API"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)