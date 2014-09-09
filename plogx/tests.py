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
            'timestamp': datetime(2013, 10, 13),
            'ip_address': "127.0.0.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 10, 12, 0, 0),
            'ip_address': "192.168.1.1"
            },{
            'path': u'/def',
            'timestamp': datetime(2013, 10, 12, 23, 59),
            'ip_address': "192.168.1.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 8, 12),
            'ip_address': "127.0.0.1"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 10, 12),
            'ip_address': "192.168.1.2"
            },{
            'path': u'/abc',
            'timestamp': datetime(2013, 10, 12),
            'ip_address': "192.168.1.2"
            }]
        self.ids = self.db.log_items.insert(self.dummy_log_items)

    def test_stats_per_day(self):
        day = datetime(2013, 10, 12, 23, 44)
        stats = database.get_stats_per_day(self.db, day)

        stats_db = self.db.stats_per_day.find_one({
            "_id": datetime.combine(day, datetime.min.time())})
        self.assertIsNotNone(stats_db)

        dummy_stats = []
        for item in self.dummy_log_items:
            if item["timestamp"].date() == day.date():
                dummy_stats.append((item["path"], item["ip_address"]))

        self.assertEqual(stats["num_page_impressions"],len(set(dummy_stats)))

    def test_stats_per_month(self):
        month = datetime.combine(datetime(2013, 10, 01), datetime.min.time())

        # check, if the stats for past month 10 get saved in log_db.stats_per_month
        stats = database.get_stats_per_month(self.db, month)
        self.assertIsNotNone(self.db.stats_per_month.find_one({"_id": month}))

        # check, if the days are in correct order
        for day in range(1,30):
            self.assertEqual(stats["day_stats"][day-1]["day"],\
                datetime(2013, 10, day))

        # check, if the stats for october 12th are correct
        day_stats = stats["day_stats"][11]
        self.assertEqual(day_stats["num_page_impressions"], 3)
        self.assertEqual(day_stats["num_visits"], 2)

        # get correct values for months without any visits
        stats = database.get_stats_per_month(self.db, datetime(1999, 1, 1))
        self.assertEqual(stats["num_page_impressions"], 0)
        self.assertEqual(stats["num_visits"], 0)

        # the stats document should not be saved in log_db.stats_per_month
        # for the current month
        month = datetime.combine(datetime.now(), datetime.min.time())
        stats = database.get_stats_per_month(self.db, month)
        self.assertIsNone(self.db.get_stats_per_month.find_one({"_id": month}))

    def test_stats_per_path_per_month(self):
        month = datetime.combine(datetime(2013, 10, 01), datetime.min.time())
        stats = database.get_stats_per_month(self.db, month)

        # get correct values for number of path visits
        self.assertEqual(stats["path_stats"]["/abc"], 3)
        self.assertEqual(stats["path_stats"]["/def"], 1)

    def test_raw_logs_per_day(self):
        day = datetime.combine(datetime(2013, 10, 12), datetime.min.time())

        items = [x for x in self.dummy_log_items \
            if x["timestamp"].date() == day.date()]
        items_db = [x for x in database.get_raw_logs_per_day(self.db, day)]

        # check if the number of items matches the number of items retreived
        self.assertEqual(len(items), len(items_db))

        # check if the function returns a Cursor
        for item in items:
            self.assertTrue(item in items_db)

    def tearDown(self):
        self.db.log_items.remove()
        self.db.stats_per_day.remove()
        self.db.stats_per_month.remove()

if __name__ == '__main__':
    unittest.main()