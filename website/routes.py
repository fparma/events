from flask import render_template, session, redirect, flash, url_for, request, json, g
from functools import wraps

from website import app, oid
from website.database import get_steam_userinfo, Ban, Event, Slot, Side, Group, User, db
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
    if Ban.query.filter_by(steam_id=match.group(1)).first() is not None:
        flash('Your SteamID is banned.')
        return redirect(url_for('index'))
    g.user = User.get_or_create(match.group(1))
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    flash('You are logged in as %s' % g.user.nickname)
    return redirect(oid.get_next_url())

@app.route('/')
def index():
    coming_events = Event.query.all()
    return render_template('index.html', events=coming_events)

@app.route('/<evid>')
def event(evid):
    ev = Event.query.filter_by(id=evid).first_or_404()
    return render_template('event-page.html', event=ev)

@app.route('/create', methods=['GET','POST'])
def create_event():
    if request.method == 'POST':
        event_json = request.json
        return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('event-create.html')

@app.before_request
def create_mock_event():
    if Event.query.all() == []:
        slot = Slot(title="Platoon Leader")
        group = Group(title="Lawman One", slots=[slot])
        side = Side(title="West", groups=[group])
        new_event = Event(title="C025 - The Bog", event_type="CO", description="Following an ambush that left half of the platoon destroyed, the remaining men in Lawman Company move out to save the only survivors, a mobility-killed Abrams tank, stranded in the middle of hostile territory. Their job is to fight their way to the tank, repair it, and escort it back to base. Obviously based on CoD4 because goddamn that game was sick.", image_url="http://i.cubeupload.com/1rlvG0.png", sides=[side])
        db.session.add(new_event)
        db.session.commit()
