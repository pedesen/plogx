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
        self.ids = self.db.log_items.insert(self.dummy_log_items)


    def test_stats_per_day(self):
        day = datetime(2013, 11, 12, 23, 44)
        stats = database.get_stats_per_day(self.db, day)

        self.assertEqual(
            stats["num_page_impressions"],
            len(set([(x["path"], x["ip_address"]) \
                for x in self.dummy_log_items])))

        self.assertEqual(
            stats["num_visits"],
            len(set([x["ip_address"] for x in self.dummy_log_items])))
        

    def tearDown(self):
        self.db.log_items.remove()
        self.db.stats_per_day.remove()
        self.db.stats_per_month.remove()

if __name__ == '__main__':
    unittest.main()