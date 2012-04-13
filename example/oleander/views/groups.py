# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, abort, jsonify
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.ajax import ajax_only, template_to_html
from oleander.models import Group
from oleander.forms import GroupForm


@app.route('/groups/')
@app.route('/groups/<any(new):action>/', methods=('GET', 'POST'))
@app.route('/groups/<any(edit):action>/<int:id>', methods=('GET', 'POST'))
@login_required
def groups(action=None, id=None):
    """Groups index."""
    group = current_user.group_or_404(id) if id else None
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
@ajax_only
def search_contacts(term):
    contacts = []
    for contact in current_user.search_contacts(term, limit=6):
        contact_dict = contact.to_dict()
        contact_dict['html_search_result'] = template_to_html('_contact_box.html', contact=contact, term=term)
        contact_dict['html'] = template_to_html('_contact_box.html', contact=contact)
        contacts.append(contact_dict)
    return jsonify(term=term, contacts=contacts)



@app.route('/groups/delete/<int:id>')
@login_required
def delete_group(id):
    """Removes group by ID."""
    with db.transaction as session:
        current_user.group_or_404(id).delete()
    return redirect(url_for('groups'))


@app.route('/group/<int:id>')
@app.route('/group/<any(edit):action>/<int:id>', methods=('GET', 'POST'))
@login_required
def group(id, action=None):
    """Group page."""
    group = current_user.group_or_404(id)
    form = GroupForm(obj=group) if action else None

    if form and form.validate_on_submit():
        with db.transaction as session:
            form.populate_obj(group)
        return redirect(url_for('group', id=id))

    return render_template('group.html', group=group, action=action, form=form)


