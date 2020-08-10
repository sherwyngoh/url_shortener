import time
import os
import validators
import humanfriendly

from flask import abort, Flask, request, jsonify
from storage.interface import Storage

BASE_URL = 'http://example.com/'
URL_NOT_PROVIDED = "URL not provided"
INVALID_URL = "Invalid URL provided"
INVALID_SHORTPATH = "Invalid short path provided"
URL_NOT_FOUND = "URL not found. It may have expired."
ERROR_500 = "Something went wrong, please try again in awhile"


app = Flask(__name__)

store = Storage()

@app.route("/")
def healthcheck():
  return 'ok'


@app.route('/create_short_url', methods=["POST"])
def create_short_url():
    url = request.get_json().get('url')

    if not url:
      abort(400, description=URL_NOT_PROVIDED)
    
    if not validators.url(url):
      abort(400, description=INVALID_URL)

    try:
      key, cache_expiry = store.append(url)
      return jsonify({"url": BASE_URL + key, "expires_in": humanfriendly.format_timespan(cache_expiry)}), 201

    except Exception as e:
      print(e)
      return abort(500, description=ERROR_500)


@app.route('/get_long_url', methods=["POST"])
def get_long_url():
    url = request.get_json().get('url')

    if not url:
        abort(404, description=URL_NOT_PROVIDED)
    
    if not validators.url(url):
        abort(404, description=INVALID_URL)

    short_path = url.split('/')[-1]

    if len(short_path) is not Storage.SHORTPATH_LENGTH:
        abort(400, description=INVALID_SHORTPATH)

    try:
        result = store.get(short_path)
        if not result:
            return jsonify(URL_NOT_FOUND), 404

        return jsonify({"url": result['result'], "expires_in": humanfriendly.format_timespan(result['ttl'])})

    except Exception as e:
        return abort(500, ERROR_500)