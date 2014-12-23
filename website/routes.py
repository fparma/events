from flask import send_from_directory, render_template, session, redirect, flash, url_for, request, json, g

from website import app, oid
from werkzeug import secure_filename
from werkzeug.exceptions import BadRequest
from website.database import get_steam_userinfo, Ban, Event, Slot, Side, Group, User, db

from functools import wraps
import os, re, json as pjson


_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')


def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def admin_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not g.user.is_admin:
			flash('You need admin privileges to access this area.')
			return redirect(url_for('index', next=request.url))
		return f(*args, **kwargs)
	return decorated_function


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
	steam_id = match.group(1)
	if Ban.query.get(steam_id) is not None:
		flash('Your SteamID is banned.')
		return redirect(url_for('index'))
	g.user = User.get_or_create(steam_id)
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
	ev = Event.query.get_or_404(evid)
	#print(pjson.dumps(ev.as_dict()))
	return render_template('event-page.html', event=ev)


@app.route('/assign/<int:slotid>', methods=['POST'])
@login_required
def event_signup(slotid):
	slot = Slot.query.get_or_404(slotid)
	print(slot.occupant)
	if slot.occupant is None:
		slot.occupant = g.user
		db.session.add(slot)
		db.session.commit()
		return redirect(url_for('index'))
	elif slot.occupant.id == g.user.id:
		slot.occupant = None
		db.session.add(slot)
		db.session.commit()
		return redirect(url_for('index'))
	else:
		return redirect(url_for('index'), 403)

@app.route('/create', methods=['GET', 'PUT', 'POST'])
@login_required
@admin_required
def create_event():
	if request.method in ['PUT', 'POST']:
		event_json = request.get_json()

		if event_json is None:
			raise BadRequest(description="Invalid JSON!")

		new_event = Event()
		# if request.method == 'POST':
		#    event_id = event_json.get('eventId')
		#    new_event = Event.query.filter_by(id=event_id).first()

		new_event.creator = g.user
		new_event.title = event_json.get('eventNameFull')
		new_event.image_url = event_json.get('eventImageUrl')
		new_event.description = event_json.get('eventDescription')
		new_event.slot_count = event_json.get('eventSlotsNumber')

		sides = []
		for side, groups in event_json.get('eventSlots').items():
			new_side = Side(title=side)
			new_groups = []

			for group in groups:
				new_grp = Group(title=group.get('name'))
				new_grp.slots = [Slot(title=unit.get('role'), group=new_grp)
						for unit in group.get('units')]
				new_groups.append(new_grp)

			new_side.groups = new_groups
			sides.append(new_side)

		new_event.sides = sides
		db.session.add(new_event)
		db.session.commit()
		return redirect(url_for('index'), code=302)
	elif request.method == 'GET':
		return render_template('event-create.html')


@app.route('/upload', methods=['POST'])
@login_required
@admin_required
def upload_file():
	'''Takes a file by POST, returns the absolute URL to the uploaded file.'''

	def filename_exists(path, fname):
		'''Adds 1 to the end of a filename until it
		finds one which does not exist'''
		if os.path.exists(os.path.join(path, fname)):
			fn, ext = os.path.splitext(fname)
			return filename_exists(path, fn + "1" + ext)
		else:
			return fname

	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			new_filename = filename_exists(app.config['UPLOAD_FOLDER'], filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
			return url_for('uploaded_file', filename=new_filename, _external=True)


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
