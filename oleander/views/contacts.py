# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, request, flash, session
from flask.ext.login import login_required, current_user
from oleander import app, db, facebook, google
from oleander.forms import EmailContactForm
from oleander.models import Contact, FacebookContact, GoogleContact, EmailContact
from gdata.contacts.client import ContactsQuery


def create_email_contact(email):
    if email.endswith(('gmail.com', 'googlemail.com')):
        return GoogleContact()
    return EmailContact()


@app.route('/contacts/', methods=('GET', 'POST'))
@login_required
def contacts():
    """Contacts management page."""
    form = EmailContactForm()

    if form.validate_on_submit():
        with db.transaction as session:
            contact = create_email_contact(form.email.data)
            form.populate_obj(contact)
            contact.user = current_user
            session.add(contact)
        return redirect(url_for('contacts'))

    contacts = current_user.contacts.order_by('name')
    return render_template('contacts.html', form=form, contacts=contacts)


@app.route('/contacts/delete/<int:id>')
@login_required
def delete_contact(id):
    """Removes contact by ID."""
    contact = current_user.get_contact_or_404(id)
    if contact.is_primary:
        flash('Cannot delete primary contact.')
    elif list(contact.attendance):
        flash('Cannot delete contact involved in events.')
    else:
        with db.transaction as session:
            current_user.delete_contact(id)
    return redirect(url_for('contacts'))


@app.route('/contacts/import/facebook')
@login_required
def import_facebook_friends():
    try:
        api = facebook.create_api()
        me = api.get('me')

        friends = api.get('me/friends')['data']
        friends.append(me)

        for friend in friends:
            with db.transaction as session:
                contact = current_user.find_facebook_contact(friend['id'])
                if not contact:
                    contact = FacebookContact()
                    contact.name = friend['name']
                    contact.facebook_id = friend['id']
                    contact.user = current_user
                    contact.belongs_to_user = friend['id'] == me['id']
                    session.add(contact)
                else:
                    contact.name = friend['name']

        return redirect(url_for('contacts'))

    except facebook.ConnectionError:
        return redirect(facebook.create_authorize_url(
            action_url=url_for('import_facebook_friends'),
            error_url=url_for('contacts')
        ))


@app.route('/contacts/import/google')
@login_required
def import_google_contacts():
    try:
        api = google.create_api(google.ContactsClient)

        group_id = None
        feed = api.GetGroups()
        for entry in feed.entry:
            if entry.title.text == 'System Group: My Contacts':
                group_id = entry.id.text

        query = ContactsQuery()
        query.max_results = 10000
        if group_id:
            query.group = group_id
        feed = api.GetContacts(q=query)

        my_emails = current_user.emails

        for entry in feed.entry:
            with db.transaction as session:
                for email in entry.email:
                    if not entry.name or not entry.name.full_name:
                        continue
                    contact = current_user.find_email_contact(email.address)
                    if not contact:
                        contact = create_email_contact(email.address)
                        contact.name = entry.name.full_name.text
                        contact.email = email.address
                        contact.user = current_user
                        contact.belongs_to_user = email.address in my_emails
                        session.add(contact)
                    else:
                        contact.name = entry.name.full_name.text

        return redirect(url_for('contacts'))

    except google.ConnectionError:
        return redirect(google.create_authorize_url(
            action_url=url_for('import_google_contacts'),
            error_url=url_for('contacts'),
            scope='https://www.google.com/m8/feeds/'
        ))