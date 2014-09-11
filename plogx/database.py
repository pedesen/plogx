from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
import re
try:
    import config
except ImportError:
    import config_example as config



def _aggregate_day_stats(db, log_day):

    start_date = log_day
    end_date = start_date + timedelta(days=1)

    excluded_clients = []
    if config.excluded_clients:
        excluded_clients = [re.compile(x) for x in config.excluded_clients]

    match_filter = {
        "timestamp": {
            "$gte": start_date,
            "$lt": end_date
        },
        "path": {
            "$nin": config.excluded_paths
        },
        "ip_address": {
            "$nin": config.excluded_ips
        },
        "client": {
            "$nin": excluded_clients
        }
    }

    page_impressions = db.log_items.aggregate([
        # match and filter all documents for the specified day
        {"$match": match_filter},
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


def _aggregate_month_stats(db, log_month):
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
        get_stats_per_day(db, current_day)

    day_stats = db.stats_per_day.aggregate([
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


def get_stats_per_day(db, log_day):
    """
    Generates a stats document, which includes the number of page impressions,
    the total number of visits and a list of path/ip-address combinations
    for one specific day. This document gets saved in log_db.stats_per_day,
    unless log_day is doday.
    @return stats document [dict]
    """
    log_day = datetime.combine(log_day.date(), datetime.min.time())
    stats_document = db.stats_per_day.find_one({"_id": log_day})
    if not stats_document or datetime.now().date() == log_day.date():
        # If no document is saved for the specified day, genereate one.
        # if the specific day is today, the document will always be generated.
        stats_document = _aggregate_day_stats(db, log_day)
        try:
            db.stats_per_day.insert(stats_document)
        except DuplicateKeyError:
            date = stats_document["_id"]
            del(stats_document["_id"])
            db.stats_per_day.update({"_id": date}, {"$set": stats_document})

    return stats_document

def get_stats_per_month(db, log_month):
    stats_document = db.stats_per_month.find_one({"_id": log_month})
    if not stats_document:
        stats_document = _aggregate_month_stats(db, log_month)
        if datetime.now().strftime("%Y%m") != log_month.strftime("%Y%m"):
            db.stats_per_month.insert(stats_document)
    return stats_document

def get_raw_logs_per_day(db,log_day):
    """
    @return: a cursor containing all log items for the specified day in reverse order
        [pymongo.cursor.Cursor]
    """
    start_date = datetime.combine(log_day.date(), datetime.min.time())
    end_date = start_date + timedelta(days=1)
    return db.log_items.find({"timestamp": {"$gte": start_date, "$lt": end_date}}).sort("timestamp", -1)
