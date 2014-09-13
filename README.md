plogx
=====

plogx is a Flask webapp, which analyses, filters and visualizes nginx log items stored in a mongodb database

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

### Quick Start (Development Server)

Please don't use this in production!

```
source env/bin/activate
python plogx/app.py
```
