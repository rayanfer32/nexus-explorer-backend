import os
import flask
import requests
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
import requests_cache
from api import blockEstimatorApi
from api import chartApi

from dotenv import load_dotenv
config = load_dotenv("local.env")

print("config:", config)

app = Flask('__main__')
cors = CORS(app)
method_requests_mapping = {
    'GET': requests.get,
    'HEAD': requests.head,
    'POST': requests.post,
    'PUT': requests.put,
    'DELETE': requests.delete,
    'PATCH': requests.patch,
    'OPTIONS': requests.options,
}
SERVER_URL = os.getenv("SERVER_URL").rstrip('/')
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

block_estimator = blockEstimatorApi.BlockEstimator()

# install cache provider for requests
requests_cache.install_cache(
    'nexusapi_cache', backend='sqlite', expire_after=15)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=method_requests_mapping.keys())
@cross_origin()
def proxy(path):
    if request.method == "OPTIONS":  # CORS preflight
        return _build_cors_preflight_response()
    else:
        resp = requests.request(method=request.method, url=f'{SERVER_URL}/{path}',
                                headers=request.headers, params=request.args, data=request.data, json=request.json)
        return _corsify_actual_response(resp)


@app.route('/chart')
@cross_origin()
def handleChartApi():
    return chartApi.getChartData(2)


@app.route('/blockFromTimestamp/<timestamp>')
@cross_origin()
def handleBlockFromTimestamp(timestamp):
    timestamp = int(timestamp)
    try:
        estimated_block, error = block_estimator.findBlockFromTimestamp(
            timestamp)
        return {'estimatedBlock': estimated_block, "error": error}
    except Exception as e:
        return {'error': 'invalid timestamp'}


def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


def _corsify_actual_response(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response.json()


def main():
    app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    app.debug = True
    main()
