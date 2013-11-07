from flask import Flask
from flask import render_template
from flask.ext.pymongo import PyMongo
import database
from bson.json_util import dumps
from datetime import datetime

app = Flask("log_db")
mongo = PyMongo(app)
app.debug = True

@app.route('/')
def overview():
    return render_template('index.html')

@app.route('/all_items')
def all_items():
    return dumps(database.all_log_items(mongo.db))

if __name__ == "__main__":
    app.run()