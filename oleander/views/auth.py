# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, request
from flask.ext.login import login_required, login_user, logout_user
from oleander import app, db, login_manager
from oleander.forms import SignUpForm, SignInForm
from oleander.models import User


@login_manager.user_loader
def load_user(user_id):
    """User loader used by sign-in process."""
    return User.query.filter_by(id=user_id).first()


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