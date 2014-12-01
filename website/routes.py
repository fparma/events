from flask import render_template, session, redirect, flash, url_for, request, g
from functools import wraps

from website import app, oid
from website.database import get_steam_userinfo, Event, Slot, User, db
from website.forms import EventForm

import re

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(oid.get_next_url())

@app.route('/login')
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')

@oid.after_login
def create_or_login(resp):
    match = _steam_id_re.search(resp.identity_url)
    g.user = User.get_or_create(match.group(1))
    print(match.group(1))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    flash('You are logged in as %s' % g.user.nickname)
    return redirect(oid.get_next_url())

@app.route('/')
def index():
    coming_events = Event.query.all()
    slot_count = len(coming_events.slots)
    return render_template('index.html', events=coming_events, count=slot_count)

@app.route('/<evid>')
def event(evid):
    ev = Event.query.filter_by(id=evid).first_or_404()
    return render_template('event-page.html', event=ev)

@app.route('/create')
def create_event():
    form = EventForm()
    return render_template('event-create.html', form=form)

@app.before_request
def create_mock_event():
    if Event.query.all() == []:
        slot1 = Slot(title="Platoon Leader")
        new_event = Event(title="C025 - The Bog", description="Following an ambush that left half of the platoon destroyed, the remaining men in Lawman Company move out to save the only survivors, a mobility-killed Abrams tank, stranded in the middle of hostile territory. Their job is to fight their way to the tank, repair it, and escort it back to base. Obviously based on CoD4 because goddamn that game was sick.", image_url="http://i.cubeupload.com/1rlvG0.png", slots=[slot1])
        db.session.add(new_event)
        db.session.commit()
