# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.models import Group


@app.route('/groups/', methods=('GET', 'POST'))
@login_required
def groups():
    """Groups index."""
    # form = EmailContactForm()

    # if form.validate_on_submit():
    #     with db.transaction as session:
    #         contact = EmailContact()
    #         form.populate_obj(contact)
    #         contact.user = current_user
    #         session.add(contact)
    #     return redirect(url_for('groups'))

    contacts = current_user.groups
    return render_template('groups.html', groups=groups)


@app.route('/delete-group/<int:id>')
@login_required
def delete_group(id):
    """Removes group by ID."""
    with db.transaction as session:
        Group.query.filter(Group.id == id).delete()
    return redirect(url_for('groups'))