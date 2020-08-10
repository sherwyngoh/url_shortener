import redis
import uuid
import time

from datetime import timedelta


class Storage:
    DEFAULT_STORAGE = lambda: redis.Redis(host='redis', port=6379, decode_responses=True)
    DEFAULT_EXPIRY = timedelta(days=7)
    DEFAULT_RETRY_COUNT = 5
    REDIS_KEY_DOES_NOT_EXIST = -2
    SHORTPATH_LENGTH = 6

    def __init__(self, storage=DEFAULT_STORAGE):
        self.store = storage()
    

    def get_unique_id(self):
        key = str(uuid.uuid4())[:6]
        key_exists = self.store.get(key)
        while key_exists:
            key = str(uuid.uuid4())[:6]
            key_exists = self.store.get(key)
        return key

        
    def append(self, value, expiry=DEFAULT_EXPIRY):
        _id  = self.get_unique_id()
        return self.put(_id, value, expiry)

    
    def get(self, key):
        retries = Storage.DEFAULT_RETRY_COUNT
        while True:
            try:
                ttl = self.store.ttl(key)
                if ttl is Storage.REDIS_KEY_DOES_NOT_EXIST: 
                  return False
                else:
                  result = self.store.get(key)
                  return {"result": result, "ttl": ttl}
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    raise exc
                retries -= 1
                time.sleep(0.5)


    def put(self, key, value, expiry):
        retries = Storage.DEFAULT_RETRY_COUNT
        while True:
            try:
                self.store.setex(key, expiry, value)
                return [key, expiry]
            except redis.exceptions.ConnectionError as exc:
                if retries == 0:
                    raise exc
                retries -= 1
                time.sleep(0.5)
