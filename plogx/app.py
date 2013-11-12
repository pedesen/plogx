from flask import Flask
from flask import render_template
from flask.ext.pymongo import PyMongo
from database import get_stats_per_day, get_stats_per_month
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
    log_items = get_stats_per_day(mongo.db, day)
    return dumps(log_items)

@app.route("/stats_per_month/<int:date>")
def stats_per_month(date):
    d = str(date)
    month = datetime(int(d[:4]), int(d[4:6]), 1)
    log_items = get_stats_per_month(mongo.db, month)
    return dumps(log_items)

if __name__ == "__main__":
    app.run()