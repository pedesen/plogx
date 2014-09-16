plogx
=====

plogx is a Flask webapp written in Python, which analyses, filters and visualizes nginx log items stored in a mongodb database. Please see my blog for a more detailed description: http://blog.pedesen.de/2014/09/15/analyze-and-visualize-nginx-log-data-with-parsible-and-plogx/

![plogx screenshot](http://www.pedesen.de/images/plogx_screenshot.png)

### Installation

```
git clone https://github.com/pedesen/plogx.git
cd plogx
virtualenv env
source env/bin/activate
pip install -r requirements
deactivate
```

### Quick Start

plogx expects a running mongo daemon with a database named `log_db` and a collection named `log_items`.

Because plogx needs existing log data in the database, you have to take care of that. To collect log data in realtime and store them into a database, you can use my fork of [parsible](https://github.com/pedesen/parsible), which works great with nginx logs and mongodb. But you can also write your own parsible-plugins for other webservers like Apache.

#### Start development server

Please don't use this in production! Always serve the flask app with uwsgi and nginx or Apache for example and secure it with basic auth:
```
source env/bin/activate
python plogx/app.py
```
