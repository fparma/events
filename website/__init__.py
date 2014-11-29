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

@app.errorhandler(403)
def not_authorized(path):
    return render_template('status/403.html'), 403

@app.errorhandler(404)
def page_not_found(path):
    return render_template('status/404.html'), 404

@app.errorhandler(410)
def resource_gone(path):
    return render_template('status/410.html'), 410

if __name__ == '__main__':
    app.run()
