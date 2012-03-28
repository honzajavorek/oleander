# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, flash, request
from flask.ext.login import login_required, fresh_login_required, login_user, logout_user
from oleander import app, db
from oleander.forms import SignUpForm, SignInForm
from oleander.models import User


@app.route('/')
@login_required
def index():
    """Index view, dashboard."""
    return render_template('index.html')


@app.route('/sign-up/', methods=('GET', 'POST'))
def sign_up():
    """Registration form."""
    form = SignUpForm()
    if form.validate_on_submit():
        user = User()
        with db.transaction as session:
            form.populate_obj(user)
            session.add(user)
        return redirect(url_for('sign_in'))
    return render_template('sign_up.html', form=form)


@app.route('/sign-in/', methods=('GET', 'POST'))
def sign_in():
    """Sign in view."""
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user:
            form.add_error('email', 'There is no such user.')
        elif not user.check_password(form.password.data):
            form.add_error('password', 'Password is invalid.')
        elif login_user(user, remember=True):
            return redirect(request.args.get('next') or url_for('index'))

    return render_template('sign_in.html', form=form)


@app.route('/sign-out/')
@login_required
def sign_out():
    """Simple sign out view."""
    logout_user()
    return redirect(url_for('sign_in'))


@app.route('/settings/')
@fresh_login_required
def settings():
    """Minimalist settings page."""
    return render_template('settings.html')
