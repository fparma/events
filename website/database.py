from flask.ext.sqlalchemy import SQLAlchemy
from urllib.request import urlopen
from urllib.parse import urlencode
import codecs
import json

from website import app
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

class Ban(db.Model):
    __tablename__ = "ban"

    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(48))

class User(db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(48))
    registration_date = db.Column(db.DateTime,
        default=db.func.current_timestamp())
    
    events = db.relationship('Event', 
            backref=db.backref('creator'))
    slots = db.relationship('Slot',
            backref=db.backref('occupant'))
    
    nickname = db.String(128)
    
    # [TODO] track timezone, have a default value.

    @staticmethod
    def get_or_create(steam_id):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            db.session.add(rv)
        return rv

class Event(db.Model):

    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(256))
    event_type = db.Column(db.String(16))
    
    scheduled_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime, 
        default=db.func.current_timestamp())

    sides = db.relationship('Side',
        backref=db.backref('side'))

class Slot(db.Model):

    __tablename__ = "slot"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    occupant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment = db.Column(db.String(256))

class Group(db.Model):

    __tablename__ = "group"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    side_id = db.Column(db.Integer, db.ForeignKey('side.id')) 
    
    slots = db.relationship('Slot',
        backref=db.backref('group'))

class Side(db.Model):

    __tablename__ = "side"

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    title = db.Column(db.String(16))
    
    groups = db.relationship('Group',
        backref=db.backref('side'))
