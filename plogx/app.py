from flask import Flask
from flask import render_template
from flask import request
from bson.json_util import dumps
from datetime import datetime
from database import Aggregator

app = Flask("log_db")
aggregator = Aggregator(app)
app.debug = True

@app.route("/")
@app.route("/stats/<int:date>")
def overview(date=None):
    if date is None:
        now = datetime.now()
        date = "{0}{1:0>2}".format(now.year, now.month)
    return render_template("stats.html", date=date)

@app.route("/raw_logs_per_day/<int:date>")
def raw_logs_per_day(date):
    filter_items = False 
    if request.args.get('filter') == "true":
        filter_items = True
    d = str(date)
    day = datetime(int(d[:4]), int(d[4:6]), int(d[6:]))
    log_items = aggregator.get_raw_logs_per_day(day, filter_items)
    return render_template("raw_logs_per_day.html",
        log_items=log_items, date=date, filter_items = filter_items)

@app.route("/stats_per_day/<int:date>")
def stats_per_day(date):
    d = str(date)
    day = datetime(int(d[:4]), int(d[4:6]), int(d[6:]))
    log_items = aggregator.get_stats_per_day(day)
    return dumps(log_items)

@app.route("/stats_per_month")
@app.route("/stats_per_month/<int:date>")
def stats_per_month(date=None):
    if date is None:
        now = datetime.now()
        month = datetime(now.year, now.month, 1)
    else:
        d = str(date)
        month = datetime(int(d[:4]), int(d[4:6]), 1)
    log_items = aggregator.get_stats_per_month(month)
    return dumps(log_items)

if __name__ == "__main__":
    app.run()