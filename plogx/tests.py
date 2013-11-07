import unittest
from pymongo import MongoClient
from datetime import datetime, timedelta
import database

class TestMongoDBFunctions(unittest.TestCase):

    def setUp(self):
        self.client = MongoClient()
        self.db = self.client.test_db
        self.dummy_log_items = [{
            'path': u'/abc',
            'timestamp': datetime(2013, 11, 13),
            'ip_address': "127.0.0.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 11, 12, 0, 0),
            'ip_address': "192.168.1.1"
            },{
            'path': u'/def',
            'timestamp': datetime(2013, 11, 12, 23, 59),
            'ip_address': "192.168.1.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 11, 12),
            'ip_address': "127.0.0.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 11, 12),
            'ip_address': "192.168.1.1"
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


    def test_get_stats_per_day(self):
        day = datetime(2013, 11, 12, 23, 44)

        # get all log_items from self.dummy_log_items, which are dated at
        # the specified day
        log_items = [x for x in self.dummy_log_items if day.date() \
            <= x['timestamp'].date() < day.date() + timedelta(days=1)]
        
        # get all log_items from the database, which are dated at the
        # specified day
        log_items_db = database.get_stats_per_day(self.db, day)

        # get a list of unique values for specific key in a log_item list
        get_values = lambda log_items, key: set([z[key] for z in log_items])

        # check for each key if the values are the same as specified in setUp
        for key in ["ip_address", "path"]:
            self.assertEqual(get_values(log_items_db, key), \
                get_values(log_items, key))

if __name__ == '__main__':
    unittest.main()