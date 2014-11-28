from flask import render_template
from website import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<evid>')
def event(evid):
    ev = Event.query.filter_by(id=evid).first_or_404()
    return render_template('event.html', ev)
