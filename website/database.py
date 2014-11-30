from flask.ext.sqlalchemy import SQLAlchemy
from website import app
from urllib.request import urlopen
from urllib.parse import urlencode
import codecs
import json

from appconf import config

app.config['SQLALCHEMY_DATABASE_URI'] = config['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(app)

def get_steam_userinfo(steam_id):
    options = {
        'key': app.config['STEAM_API_KEY'],
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
            'GetPlayerSummaries/v0001/?%s' % urlencode(options)
    reader = codecs.getreader('utf-8')
    rv = json.load(reader(urlopen(url)))
    return rv['response']['players']['player'][0] or {}

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(48))
    nickname = db.String(128)

    @staticmethod
    def get_or_create(steam_id):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            db.session.add(rv)
        return rv

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    # [TODO] timezone column with default value
    # [TODO] reference slots

class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), unique=True)
    # [TODO] reference user if slot occupied, if no user referenced, slot is free
