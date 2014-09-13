plogx
=====

plogx is a Flask webapp, which analyses nginx log items stored in a mongodb database

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

```
source env/bin/activate
python plogx/app.py
```
