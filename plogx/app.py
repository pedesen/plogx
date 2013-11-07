from flask import Flask
from flask import render_template
from flask.ext.pymongo import PyMongo
from bson.json_util import dumps

app = Flask("log_db")
mongo = PyMongo(app)

@app.route('/')
def overview():
    return render_template('index.html')

@app.route('/all_items')
def all_items():
    return dumps(mongo.db.log_items.find())

if __name__ == "__main__":
    app.run()