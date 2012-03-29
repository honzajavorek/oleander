# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, request
from flask.ext.login import fresh_login_required, current_user
from oleander import app, db
from oleander.forms import SettingsForm, PasswordForm


@app.route('/settings/', methods=('GET', 'POST'))
@fresh_login_required
def settings():
    """Minimalist settings page."""
    form = SettingsForm(obj=current_user)

    if form.validate_on_submit():
        with db.transaction:
            form.populate_obj(current_user)
        return redirect(url_for('settings'))

    return render_template('settings.html', form=form)


@app.route('/change-password/', methods=('GET', 'POST'))
@fresh_login_required
def change_password():
    """Password changing."""
    form = PasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            form.add_error('old_password', 'Old password is invalid.')
        else:
            with db.transaction:
                current_user.password = form.new_password.data
            return redirect(request.args.get('next') or url_for('settings'))

    return render_template('change_password.html', form=form)

