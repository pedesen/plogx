from pymongo.errors import DuplicateKeyError

def all_log_items(db):
    return db.log_items.find()

def aggregate_per_day(db):
    pass

def distinct_paths(db):
    paths = db.log_items.find().distinct("path")
    for path in paths:
        try:
            db.paths.insert({'_id': path})
        except DuplicateKeyError:
            pass
    return db.paths.find()

def get_all_paths(db):
    return db.log_items.find().distinct("path")