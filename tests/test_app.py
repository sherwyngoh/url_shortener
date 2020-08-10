import unittest

from app import app
from unittest.mock import MagicMock

app.config['TESTING'] = True

class StubStorage:
  def __init__(self):
      self.get = MagickMock(return_value=True)
      self.append = MagickMock(return_value=True)


random_url = 'http://some.random.url.com/123'


class TestClient(unittest.TestCase):
    client = app.test_client()

    def test_health_check(self):
        res = TestClient.client.get('/')
        self.assertEqual(res.status_code, 200)

    
    def test_create_short_url(self):
        url = random_url
        data = dict(url=url)
        res = TestClient.client.post("/create_short_url", json=data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json['url'])
    
    
    def test_get_long_url(self):
        url = random_url
        data = dict(url=url)
        res = TestClient.client.post("/create_short_url", json=data)
        short_url = res.json['url']
        data = dict(url=short_url)
        res = TestClient.client.post("/get_long_url", json=data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['url'], url)
    

    
