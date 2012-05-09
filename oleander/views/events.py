# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, abort, jsonify
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.ajax import ajax_only, template_to_html
from oleander.models import Event
from oleander.forms import EventForm


@app.route('/events/')
@app.route('/events/<any(new):action>/', methods=('GET', 'POST'))
@app.route('/events/<any(edit):action>/<int:id>', methods=('GET', 'POST'))
@login_required
def events(action=None, id=None):
    """Events index."""
    event = current_user.event_or_404(id) if id else None
    form = EventForm(obj=event)

    if form.validate_on_submit():
        with db.transaction as session:
            if event:
                # editation
                form.populate_obj(event)

            else:
                # creation
                event = Event()
                form.populate_obj(event)
                event.user = current_user
                session.add(event)

        return redirect(url_for('events'))

    events = current_user.events
    return render_template('events.html', action=action, edited_event=event, events=events, form=form)


@app.route('/events/search-contacts/<string:term>')
@ajax_only
@login_required
def search_contacts(term):
    contacts = []
    for contact in current_user.search_contacts(term, limit=6):
        contact_dict = contact.to_dict()
        contact_dict['html_search_result'] = template_to_html('_contact_box.html', contact=contact, term=term)
        contact_dict['html'] = template_to_html('_contact_box.html', contact=contact)
        contacts.append(contact_dict)
    return jsonify(term=term, contacts=contacts)



@app.route('/events/delete/<int:id>')
@login_required
def delete_event(id):
    """Removes event by ID."""
    with db.transaction as session:
        current_user.event_or_404(id).delete()
    return redirect(url_for('events'))


@app.route('/event/<int:id>', defaults={'attendance_group': 'yes'})
@app.route('/event/<int:id>/rsvp/<any(maybe,no):attendance_group>')
def event(id, attendance_group):
    """Public event page."""
    event = Event.fetch_or_404(id)
    return render_template('event.html', event=event, attendance_group=attendance_group)


@app.route('/event/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_event(id):
    """Event editing."""
    event = current_user.event_or_404(id)
    form = EventForm(obj=event)

    if form and form.validate_on_submit():
        with db.transaction as session:
            form.populate_obj(event)
        return redirect(url_for('event', id=id))

    return render_template('edit_event.html', event=event, action='edit', form=form)


