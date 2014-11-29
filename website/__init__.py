from flask import Flask, render_template
from flask.ext.openid import OpenID

from appconf import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config['SECRET_KEY']
app.config['STEAM_API_KEY'] = config['STEAM_API_KEY']

oid = OpenID(app, config['OPENID_STORE'], safe_roots=[])

from website.database import db

db.drop_all()
db.create_all()

from website.routes import *
from website.errorhandler import *

if __name__ == '__main__':
    app.run()
