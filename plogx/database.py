from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta

def _aggregate_day_stats(db, log_day):

    start_date = log_day
    end_date = start_date + timedelta(days=1)

    page_impressions = db.log_items.aggregate([
        # match and filter all documents for the specified day
        {"$match":
            {"timestamp": {
                "$gte": start_date,
                "$lt": end_date }}},
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
    path_stats = [{"path": k, "num_page_impression": v} for k,v in path_stats_dict.items()]

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
        current_month = datetime(log_month.year, log_month.month, day)
        get_stats_per_day(db, current_month)

    day_stats = db.stats_per_day.aggregate([
        {"$match":
            {"_id": {
                "$gte": start_date,
                "$lt": end_date }}},
        {"$project": {
            "_id": 0,
            "day": "$_id",
            "num_page_impressions": "$num_page_impressions",
            "num_visits": "$num_visits"}}
        ])["result"]

    stats_document = {
        "_id": start_date,
        "day_stats": day_stats,
        "num_page_impressions": 0,
        "num_visits": 0
    }

    for day in day_stats:
        stats_document["num_page_impressions"] += day["num_page_impressions"]
        stats_document["num_visits"] += day["num_visits"]

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
    if not stats_document:
        # If no document is saved for the specified day, genereate one.
        stats_document = _aggregate_day_stats(db, log_day)
        if datetime.now().date() != log_day.date():
            # Save the document, unless the log date is today
            db.stats_per_day.insert(stats_document)
    return stats_document


def get_stats_per_month(db, log_month):
    stats_document = db.stats_per_month.find_one({"_id": log_month})
    if not stats_document:
        stats_document = _aggregate_month_stats(db, log_month)
        if datetime.now().strftime("%Y%m") != log_month.strftime("%Y%m"):
            db.stats_per_month.insert(stats_document)
    return stats_document