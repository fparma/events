from flask import send_from_directory, render_template, session, redirect, flash, url_for, request, json, g
from functools import wraps

from website import app, oid
from werkzeug import secure_filename
from website.database import get_steam_userinfo, Ban, Event, Slot, Side, Group, User, db
import os
import re

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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
    coming_events = Event.query.order_by(Event.scheduled_date).all()
    return render_template('index.html', events=coming_events)

@app.route('/<evid>')
def event(evid):
    ev = Event.query.filter_by(id=evid).first_or_404()
    return render_template('event-page.html', event=ev)

@login_required
@app.route('/create', methods=['GET','POST'])
def create_event():
    if request.method == 'POST':
        new_event = Event()
        event_json = request.get_json()
        print(event_json)
        new_event.creator = g.user
        new_event.title = event_json['eventNameFull']
        new_event.description = event_json['eventDescription']
        new_event.slot_count = event_json['eventSlotsNumber']
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'), code=302)
    elif request.method == 'GET':
        return render_template('event-create.html')

@login_required
@app.route('/upload', methods=['POST'])
def upload_file():
    '''Takes a file by POST, returns the absolute URL to the uploaded file.'''
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return url_for('uploaded_file', filename=filename, _external=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

@app.before_request
def create_mock_event():
    if Event.query.all() == []:
        slot = Slot(title="Platoon Leader")
        group = Group(title="Lawman One", slots=[slot])
        side = Side(title="West", groups=[group])
        new_event = Event(title="C025 - The Bog", event_type="CO", description="Following an ambush that left half of the platoon destroyed, the remaining men in Lawman Company move out to save the only survivors, a mobility-killed Abrams tank, stranded in the middle of hostile territory. Their job is to fight their way to the tank, repair it, and escort it back to base. Obviously based on CoD4 because goddamn that game was sick.", image_url="http://i.cubeupload.com/1rlvG0.png", sides=[side])
        db.session.add(new_event)
        db.session.commit()
