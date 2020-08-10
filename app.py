import time
import uuid
import validators
import humanfriendly
from flask import abort, Flask, request, jsonify
from redis import Redis
from datetime import timedelta

app = Flask(__name__)
cache = Redis(host='redis', port=6379, decode_responses=True)

BASE_URL = 'http://example.com/'
URL_NOT_PROVIDED = "URL not provided"
INVALID_URL = "Invalid URL provided"
URL_NOT_FOUND = "URL not found. It may have expired."
ERROR_500 = "Something went wrong, please try again in awhile"
DEFAULT_RETRY_COUNT = 5
REDIS_KEY_DOES_NOT_EXIST = -2

def get_from_cache(key):
    retries = DEFAULT_RETRY_COUNT
    while True:
        try:
            result = cache.get(key)
            ttl = cache.ttl(key)
            if ttl is REDIS_KEY_DOES_NOT_EXIST: 
              return False
            else:
              return {"result": result, "ttl": ttl}
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


def set_to_cache(key, value):
    retries = 5
    while True:
        try:
            cache_expiry = timedelta(days=7)
            cache.setex(key, cache_expiry, value)
            return cache_expiry
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/create_short_url', methods=["POST"])
def create_short_url():
    url = request.get_json().get('url')

    if not url:
      abort(400, description=URL_NOT_PROVIDED)
    
    if not validators.url(url):
      abort(400, description=INVALID_URL)
    
    short_path = str(uuid.uuid4())[:6]

    try:
      exists = get_from_cache(short_path)

      while exists:
        short_path = str(uuid.uuid4())[:6]
        exists = get_from_cache(short_path)
      
      cache_expiry = set_to_cache(short_path, url)

      return jsonify({"url": BASE_URL + short_path, "expires_in": humanfriendly.format_timespan(cache_expiry)}), 201

    except:
      return abort(500, description=ERROR_500)


@app.route('/get_long_url', methods=["POST"])
def get_long_url():
    url = request.get_json().get('url')

    if not url:
        abort(404, description=URL_NOT_PROVIDED)
    
    if not validators.url(url):
        abort(404, description=INVALID_URL)

    short_path = url.split('/')[-1]


    try:
        result = get_from_cache(short_path)
        if not result:
            abort(404)

        return jsonify({"url": result['result'], "expires_in": humanfriendly.format_timespan(result['ttl'])})

    except Exception as e:
        if e.code == 404:
            return abort(404, description=URL_NOT_FOUND)
        return abort(500, ERROR_500)