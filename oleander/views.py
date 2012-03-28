# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, flash
from oleander import app, db
from oleander.forms import SignUpForm
from oleander.models import User


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign-up/', methods=('GET', 'POST'))
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        user = User()
        with db.transaction as session:
            form.populate_obj(user)
            session.add(user)
        return redirect(url_for('index'))
    return render_template('sign_up.html', form=form)


@app.route('/sign-in/')
def sign_in():
    return 'Login'