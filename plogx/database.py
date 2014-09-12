from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
import re
from flask.ext.pymongo import PyMongo
try:
    import config
except ImportError:
    import config_example as config

class Aggregator:
    def __init__(self, app):
        self.mongo = PyMongo(app)
        self.excluded_paths = config.excluded_paths
        self.excluded_ips = config.excluded_ips
        self.excluded_clients = config.excluded_clients
        self.filter = {}

    def _set_filter(self, start_date=None, end_date=None):
        if start_date:
            if "timestamp" in self.filter:
                self.filter["timestamp"]["$gte"] = start_date
            else:
                self.filter["timestamp"] = {"$gte": start_date}
            if end_date:
                self.filter["timestamp"]["$lt"] = end_date
            else:
                self.filter["timestamp"] = {"$lt": end_date}
        if self.excluded_paths:
            self.filter["path"] = {"$nin": self.excluded_paths}
        if self.excluded_ips:
            self.filter["ip_address"] = {"$nin": self.excluded_ips}
        if self.excluded_clients:
            self.filter["client"] = {"$nin": [re.compile(x) for x in self.excluded_clients]}

    def _aggregate_day_stats(self, log_day):

        start_date = log_day
        end_date = start_date + timedelta(days=1)

        self._set_filter(start_date, end_date)
        page_impressions = self.mongo.db.log_items.aggregate([
            # match and filter all documents for the specified day
            {"$match": self.filter},
            {"$group": {
                "_id": {
                    "ip_address": "$ip_address",
                    "path": "$path"},
                "timestamp": {"$min": "$timestamp"}}},
            {"$project": {
                "_id": 0,
                "path": "$_id.path",
                "ip_address": "$_id.ip_address",
                "timestamp": 1 }}])["result"]

        # counts each unique ip address
        num_visits = len(set([x["ip_address"] for x in page_impressions]))
        
        path_stats_dict = {}
        for page_impression in page_impressions:
            path = page_impression["path"]
            if path not in path_stats_dict:
                path_stats_dict[path] = 1
            else:
                path_stats_dict[path] += 1
        path_stats = [{"path": k, "num_visits": v} \
            for k,v in path_stats_dict.items()]
        path_stats = sorted(path_stats, key=lambda x: -x["num_visits"])

        stats_document = {
            "_id": start_date,
            "num_visits": num_visits,
            "num_page_impressions": len(page_impressions),
            "path_stats": path_stats
            }
        return stats_document


    def _aggregate_month_stats(self, log_month):
        start_date = datetime(log_month.year, log_month.month, 1)
        
        # determine year and month number for the next month
        year = log_month.year + start_date.month / 12
        month = start_date.month % 12 + 1
        
        # end date is the first day of the next month
        end_date = datetime(year, month, 1)
        
        # determine the last day number of the current month
        last_day = (end_date - timedelta(days = 1)).day

        # aggregate day stats for each day of the month
        for day in range(1, last_day + 1):
            current_day = datetime(log_month.year, log_month.month, day)
            self.get_stats_per_day(current_day)

        day_stats = self.mongo.db.stats_per_day.aggregate([
            {"$match":
                {"_id": {
                    "$gte": start_date,
                    "$lt": end_date }}},
            {"$project": {
                "_id": 0,
                "day": "$_id",
                "num_page_impressions": "$num_page_impressions",
                "num_visits": "$num_visits",
                "path_stats": "$path_stats"}}
            ])["result"]

        stats_document = {
            "_id": start_date,
            "day_stats": day_stats,
            "num_page_impressions": 0,
            "num_visits": 0,
            "path_stats": None
        }

        path_stats_dict = {}
        for day in day_stats:
            stats_document["num_page_impressions"] += day["num_page_impressions"]
            stats_document["num_visits"] += day["num_visits"]

            for path in day["path_stats"]:
                pathname = path["path"]
                if pathname not in path_stats_dict:
                    path_stats_dict[pathname] = path["num_visits"]
                else:
                    path_stats_dict[pathname] += path["num_visits"]
            

        path_stats = [{"path": k, "num_visits": v} \
            for k,v in path_stats_dict.items()]
        path_stats = sorted(path_stats, key=lambda x: -x["num_visits"])
        stats_document["path_stats"] = path_stats
        return stats_document


    def get_stats_per_day(self, log_day):
        """
        Generates a stats document, which includes the number of page impressions,
        the total number of visits and a list of path/ip-address combinations
        for one specific day. This document gets saved in log_db.stats_per_day,
        unless log_day is doday.
        @return stats document [dict]
        """
        log_day = datetime.combine(log_day.date(), datetime.min.time())
        stats_document = self.mongo.db.stats_per_day.find_one({"_id": log_day})
        if not stats_document or datetime.now().date() == log_day.date():
            # If no document is saved for the specified day, genereate one.
            # if the specific day is today, the document will always be generated.
            stats_document = self._aggregate_day_stats(log_day)
            try:
                self.mongo.db.stats_per_day.insert(stats_document)
            except DuplicateKeyError:
                date = stats_document["_id"]
                del(stats_document["_id"])
                self.mongo.db.stats_per_day.update({"_id": date}, {"$set": stats_document})

        return stats_document

    def get_stats_per_month(self, log_month):
        stats_document = self.mongo.db.stats_per_month.find_one({"_id": log_month})
        if not stats_document:
            stats_document = self._aggregate_month_stats(log_month)
            if datetime.now().strftime("%Y%m") != log_month.strftime("%Y%m"):
                self.mongo.db.stats_per_month.insert(stats_document)
        return stats_document

    def get_raw_logs_per_day(self, log_day, filter_items):
        """
        @return: a cursor containing all log items for the specified day in reverse order
            [pymongo.cursor.Cursor]
        """
        start_date = datetime.combine(log_day.date(), datetime.min.time())
        end_date = start_date + timedelta(days=1)
        if filter_items:
            self._set_filter(start_date, end_date)
            log_filter = self.filter
        else:
            log_filter = {"timestamp": {"$gte": start_date, "$lt": end_date}}
        return self.mongo.db.log_items.find(log_filter).sort("timestamp", -1)
