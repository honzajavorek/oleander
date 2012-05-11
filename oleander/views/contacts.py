# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, request, flash, session
from flask.ext.login import login_required, current_user
from oleander import app, db, facebook
from oleander.forms import EmailContactForm
from oleander.models import Contact, FacebookContact, GoogleContact, EmailContact


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

    except facebook.OAuthError:
        return redirect(facebook.create_authorize_url(
            action_url=url_for('import_facebook_friends'),
            error_url=url_for('contacts')
        ))

