import unittest
from pymongo import MongoClient
from datetime import datetime
import database

class TestMongoDBFunctions(unittest.TestCase):

    def setUp(self):
        self.client = MongoClient()
        self.db = self.client.test_db
        self.dummy_log_items = [{
            'path': u'/abc',
            'timestamp': datetime(2013, 11, 10, 9, 0),
            'ip': "127.0.0.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 11, 12, 8, 0),
            'ip': "192.168.1.1"
            },{
            'path': u'/def',
            'timestamp': datetime(2013, 11, 12, 8, 0),
            'ip': "192.168.1.1"
            }]
        self.all_paths = list(set([x['path'] for x in self.dummy_log_items]))
        self.all_paths.sort()
        self.ids = self.db.log_items.insert(self.dummy_log_items)

    def test_get_all_paths(self):
        all_paths = database.get_all_paths(self.db)
        all_paths.sort()
        self.assertEqual(self.all_paths, all_paths)

    def test_distinct_paths(self):
        paths = [x['_id'] for x in (database.distinct_paths(self.db))]
        paths.sort()
        self.assertEqual(self.all_paths, paths)

    def tearDown(self):
        self.db.log_items.remove()
        self.db.paths.remove()

if __name__ == '__main__':
    unittest.main()