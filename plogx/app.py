from flask import Flask
from flask import render_template
from flask.ext.pymongo import PyMongo
import database
from bson.json_util import dumps
from datetime import datetime

app = Flask("log_db")
mongo = PyMongo(app)

app.debug = True

@app.route("/")
def overview():
    return render_template("index.html")

@app.route("/stats_per_day/<int:date>")
def stats_per_day(date):
    d = str(date)
    day = datetime(int(d[:4]), int(d[4:6]), int(d[6:]))
    log_items = database.get_stats_per_day(mongo.db, day)
    return dumps(log_items)

@app.route("/raw_logs_per_day/<int:date>")
def raw_logs_per_day(date):
    d = str(date)
    day = datetime(int(d[:4]), int(d[4:6]), int(d[6:]))
    log_items = database.get_raw_logs_per_day(mongo.db, day)
    return render_template("raw_logs_per_day.html", log_items=log_items)

@app.route("/stats_per_month")
@app.route("/stats_per_month/<int:date>")
def stats_per_month(date=None):
    if date is None:
        now = datetime.now()
        month = datetime(now.year, now.month, 1)
    else:
        d = str(date)
        month = datetime(int(d[:4]), int(d[4:6]), 1)
    log_items = database.get_stats_per_month(mongo.db, month)
    return dumps(log_items)

if __name__ == "__main__":
    app.run()