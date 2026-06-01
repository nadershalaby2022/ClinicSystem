from flask import render_template

from app import app


@app.route('/tv')
def tv_screen():
    return render_template('tv/queue_screen.html')
