from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta

def all_log_items(db):
    return db.log_items.find()


def aggregate_per_day(db):
    pass


def distinct_paths(db):
    # collect all paths from all log items, distinct them and save
    # each unique path to the collection "paths"
    paths = db.log_items.find().distinct("path")
    for path in paths:
        try:
            db.paths.insert({'_id': path})
        except DuplicateKeyError:
            pass
    return db.paths.find()


def get_all_paths(db):
    """@return: unique paths found in the collection 'paths' [pymongo.cursor]"""
    if db.paths.find().count() == 0:
        distinct_paths(db)
    return [x['_id'] for x in db.paths.find()]


def get_stats_per_day(db, log_date):
    """
    Aggregate stats at a specific day grouped by ip address and path
    @return: log items [list]
    """
    # Create a start datetime object with time at 0:00
    # this is needed, because mongodb can only deal with datetime.datetime
    # objects, but not with datetime.date object types
    start = datetime.combine(log_date.date(), datetime.min.time())

    end = start + timedelta(days=1)
    
    # The aggregation pipeline consists of the three pipeline tasks
    # match, group and project
    log_items = db.log_items.aggregate([
        # match and filter all documents for the specified day
        {"$match":
            {"timestamp": {
                "$gte": start,
                "$lt": end}}},
        # group by ip address and path
        {"$group": {
            "_id": {
                "ip_address": "$ip_address",
                "path": "$path"
                },
            # first time an ip visits the path
            "timestamp": {"$min": "$timestamp"}
            },
        # reshape the output
        },{"$project": {
            "_id": 0,
            "ip_address": "$_id.ip_address",
            "path": "$_id.path",
            "timestamp" : 1
        }}
    ])
    return log_items['result']