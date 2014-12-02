from flask import Flask, render_template
from flask.ext.assets import Environment
from flask.ext.openid import OpenID

from appconf import config

app = Flask(__name__)
app.config.update(config)
assets = Environment(app)
assets.register(app.config['BUNDLES'])


oid = OpenID(app, app.config['OPENID_STORE'], safe_roots=[])

from website.database import db

db.drop_all()
db.create_all()

from website.routes import *
from website.errorhandler import *

if __name__ == '__main__':
    app.run()
