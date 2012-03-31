# -*- coding: utf-8 -*-


from flask import render_template, request, redirect, url_for, abort, jsonify
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.models import Group
from oleander.forms import GroupForm


@app.route('/groups/')
@app.route('/groups/<any(new):action>/', methods=('GET', 'POST'))
@app.route('/groups/<any(edit):action>/<int:id>', methods=('GET', 'POST'))
@login_required
def groups(action=None, id=None):
    """Groups index."""

    group = Group.query.filter(Group.id == id).first_or_404() if id else None
    form = GroupForm(obj=group)

    if form.validate_on_submit():
        with db.transaction as session:
            if group:
                # editation
                form.populate_obj(group)

            else:
                # creation
                group = Group()
                form.populate_obj(group)
                group.user = current_user
                session.add(group)

        return redirect(url_for('groups'))

    groups = current_user.groups
    return render_template('groups.html', action=action, edited_group=group, groups=groups, form=form)


@app.route('/groups/search-contacts/<string:term>')
def search_contacts(term):
    if not request.is_xhr and not app.debug:
        abort(404)
    contacts = [contact.to_dict() for contact in current_user.search_contacts(term)]
    return jsonify(term=term, contacts=contacts)



@app.route('/groups/delete/<int:id>')
@login_required
def delete_group(id):
    """Removes group by ID."""
    with db.transaction as session:
        Group.query.filter(Group.id == id).delete()
    return redirect(url_for('groups'))