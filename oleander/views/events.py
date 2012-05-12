# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, abort, jsonify
from flask.ext.login import login_required, current_user
from oleander import app, db, facebook
from oleander.ajax import ajax_only, template_to_html
from oleander.models import Event, Attendance, FacebookContact
from oleander.forms import EventForm
import operator
import datetime
import times


@app.route('/')
# @app.route('/events/<any(new):action>/', methods=('GET', 'POST'))
# @app.route('/events/<any(edit):action>/<int:id>', methods=('GET', 'POST'))
@login_required
def events():
    """Events index."""
    events = {
        'events_active': current_user.events_active.limit(3),
        'events_upcoming': current_user.events_upcoming,
        'events_past': current_user.events_past,
        'events_cancelled': current_user.events_cancelled,
    }
    events_count = sum(len(list(l)) for l in events.values())
    return render_template('events.html', events_count=events_count, **events)


@app.route('/events/create/', methods=('GET', 'POST'))
@login_required
def create_event():
    form = EventForm()

    if form.validate_on_submit():
        event = Event()
        with db.transaction as session:
            event.name = form.name.data
            event.venue = form.venue.data
            event.description = form.description.data
            event.user = current_user
            event.starts_at = times.to_universal(form.starts_at.data, current_user.timezone)
            session.add(event)
        with db.transaction:
            event.contacts_invited_ids_str = form.contacts_invited_ids_str.data
        if event.is_facebook_involved():
            return redirect(url_for('facebook_event', id=event.id))

        return redirect(url_for('event', id=event.id))

    else:
        # default starts_at
        td = datetime.timedelta(days=1)
        dt = times.to_local(times.now(), current_user.timezone) + td
        dt = datetime.datetime.combine(dt.date(), datetime.time(20, 00, 00))
        form.starts_at.data = dt

    return render_template('create_event.html', form=form)


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



@app.route('/events/cancel/<int:id>')
@login_required
def cancel_event(id):
    """Canceles event by ID."""
    event = current_user.event_or_404(id)
    with db.transaction as session:
        event.cancelled_at = times.now()
    return redirect(url_for('events'))


@app.route('/events/revive/<int:id>')
@login_required
def revive_event(id):
    """Canceles event by ID."""
    event = current_user.event_or_404(id)
    with db.transaction as session:
        event.cancelled_at = None
    return redirect(url_for('event', id=id))


@app.route('/event/<int:id>')
def event(id):
    """Public event page."""
    event = Event.fetch_or_404(id)

    if event.facebook_id and current_user.is_authenticated():
        try:
            api = facebook.create_api()
            data = api.get(path='/' + event.facebook_id + '/invited')['data']

            for friend in data:
                contact = current_user.find_facebook_contact(friend['id'])
                if not contact:
                    with db.transaction as session:
                        contact = FacebookContact()
                        contact.user = current_user
                        contact.facebook_id = friend['id']
                        contact.name = friend['name']
                        session.add(contact)
                with db.transaction:
                    event.set_attendance(contact, Attendance.types_mapping[friend['rsvp_status']])

        except facebook.ConnectionError:
            this_url = url_for('event', id=event.id)
            return redirect(facebook.create_authorize_url(
                action_url=this_url,
                error_url=this_url,
            ))

    return render_template('event.html', event=event)


@app.route('/event/edit/<int:id>', methods=('GET', 'POST'))
@login_required
def edit_event(id):
    """Event editing."""
    event = current_user.event_or_404(id)
    form = EventForm(obj=event)

    if form.validate_on_submit():
        with db.transaction as session:
            form.populate_obj(event)
            event.starts_at = times.to_universal(form.starts_at.data, current_user.timezone)
        if event.is_facebook_involved():
            return redirect(url_for('facebook_event', id=event.id))
        return redirect(url_for('event', id=event.id))

    return render_template('edit_event.html', event=event, action='edit', form=form)


@app.route('/events/facebook/<int:id>')
@login_required
def facebook_event(id):
    event = current_user.event_or_404(id)
    try:
        api = facebook.create_api()
        payload = {
            'name': event.name,
            'description': event.description or '',
            'location': event.venue or '',
            'start_time': times.format(event.starts_at, current_user.timezone, '%Y-%m-%dT%H:%M:%S'),
        }

        if event.facebook_id:
            api.post(path='/' + event.facebook_id, **payload)
        else:
            data = api.post(path='/events', **payload)
            with db.transaction:
                event.facebook_id = data['id']

        contacts_to_invite = list(event.contacts_facebook_to_invite)
        print contacts_to_invite
        if contacts_to_invite:
            ids = ','.join([c.facebook_id for c in contacts_to_invite])
            api.post(path='/' + event.facebook_id + '/invited?users=' + ids)
            with db.transaction:
                for contact in contacts_to_invite:
                    event.set_invitation_sent(contact)

        return redirect(url_for('event', id=event.id))

    except facebook.ConnectionError as e:
        return redirect(facebook.create_authorize_url(
            action_url=url_for('facebook_event', id=event.id),
            error_url=url_for('edit_event', id=event.id),
            scope='create_event'
        ))