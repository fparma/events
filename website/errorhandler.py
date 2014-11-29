from website import app

@app.errorhandler(403)
def not_authorized(path):
    return render_template('status/403.html'), 403

@app.errorhandler(404)
def page_not_found(path):
    return render_template('status/404.html'), 404

@app.errorhandler(410)
def resource_gone(path):
    return render_template('status/410.html'), 410


