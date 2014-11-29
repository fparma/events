from flask import render_template, session, redirect, g
from website import app, oid

from website.database import get_steam_userinfo, Event, User, db

import re

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

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
    steamdata = get_steam_userinfo(g.user.steam_id)
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    print('You are logged in as %s' % g.user.nickname)
    return redirect(oid.get_next_url())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<evid>')
def event(evid):
    ev = Event.query.filter_by(id=evid).first_or_404()
    return render_template('event.html', ev)
