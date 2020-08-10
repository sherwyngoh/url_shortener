import unittest
import redis

from unittest.mock import MagicMock
from storage.interface import Storage


class StubStorage:
    keys = []

    def __init__(self, ttl='ttl', get=False, setex='setex', put=['key', 'expiry']):
        self.ttl = MagicMock(return_value=ttl)
        self.get = MagicMock(return_value=get)
        self.setex = MagicMock(return_value=setex)


def stub_storage_generator():
    return StubStorage()


class TestStorage(unittest.TestCase):
    storage_instance = Storage(stub_storage_generator)

    def test_can_init(self):
        self.assertTrue(TestStorage.storage_instance)
    

    def test_assigns_store_on_init(self):
        self.assertTrue(TestStorage.storage_instance.store)
        self.assertEqual(TestStorage.storage_instance.store.ttl(), 'ttl')
    
    def test_get_unique_id(self):
        key = TestStorage.storage_instance.get_unique_id()
        self.assertTrue(len(key) == 6)

    def test_append(self):
        TestStorage.storage_instance.append(1)
        TestStorage.storage_instance.store.setex.assert_called()

    def test_get(self):
        expected_return_value = {'result': False, 'ttl': 'ttl'}
        key = 1
        return_value = TestStorage.storage_instance.get(key)
        TestStorage.storage_instance.store.ttl.assert_called_with(key)
        TestStorage.storage_instance.store.get.assert_called_with(key)
        self.assertEqual(expected_return_value, return_value)
    
    def test_put(self):
        key, value, expiry = [1,2,3]
        return_value = TestStorage.storage_instance.put(key, value, expiry)
        TestStorage.storage_instance.store.setex.assert_called_with(key, expiry, value)

    def test_retry_up_to_4_times(self):
        TestStorage.storage_instance.store.setex.side_effect = [redis.exceptions.ConnectionError()] * 4 + [True]
        key, value, expiry = [1,2,3]
        return_value = TestStorage.storage_instance.put(key, value, expiry)
        expected_return_value = [key, expiry]
        self.assertEqual(return_value, expected_return_value)
    
    def test_retry_more_than_4_times(self):
        TestStorage.storage_instance.store.setex.side_effect = [redis.exceptions.ConnectionError()] * 5 
        key, value, expiry = [1,2,3]
        with self.assertRaises(StopIteration):
            TestStorage.storage_instance.put(key, value, expiry)
    