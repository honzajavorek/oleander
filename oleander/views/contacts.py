# -*- coding: utf-8 -*-


from flask import render_template
from flask.ext.login import login_required
from flask.ext.gravatar import Gravatar
from oleander import app, db


@app.route('/contacts/', methods=('GET', 'POST'))
@login_required
def contacts():
    """Contacts management page."""
    return render_template('contacts.html')


