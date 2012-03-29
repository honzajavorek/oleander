# -*- coding: utf-8 -*-


from flask import render_template
from flask.ext.login import login_required
from oleander import app


@app.route('/')
@login_required
def index():
    """Index view, dashboard."""
    return render_template('index.html')