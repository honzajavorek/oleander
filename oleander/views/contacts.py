# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for, request, flash, session
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.forms import EmailContactForm
from oleander.models import Contact, FacebookContact, GoogleContact, EmailContact
from oauth2 import OAuth2
from facepy import GraphAPI


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

    contacts = current_user.contacts
    return render_template('contacts.html', form=form, contacts=contacts)


@app.route('/contacts/delete/<int:id>')
@login_required
def delete_contact(id):
    """Removes contact by ID."""
    with db.transaction as session:
        current_user.delete_contact(id)
    return redirect(url_for('contacts'))


def create_facebook_oauth_handler(site, action_url, error_url):
    web_hook_url = url_for(
        'facebook_connected',
        action_url=action_url,
        error_url=error_url,
        _external=True
    )
    oauth2_handler = OAuth2(
        app.config['FACEBOOK_APP_ID'],
        app.config['FACEBOOK_APP_SECRET'],
        site,
        web_hook_url,
        'dialog/oauth',
        'oauth/access_token'
    )
    return oauth2_handler


def create_facebook_authorize_url(action_url, error_url):
    oauth2_handler = create_facebook_oauth_handler('https://www.facebook.com/', action_url, error_url)
    return oauth2_handler.authorize_url()


def create_facebook_graph():
    access_token = session.get('facebook_access_token', None)
    if not access_token:
        raise GraphAPI.OAuthError('No access token.')
    return GraphAPI(access_token)


@app.route('/import/facebook')
@login_required
def import_facebook_friends():
    try:
        graph = create_facebook_graph()
        data = graph.get('me/friends')['data']

        for friend in data:
            with db.transaction as session:
                contact = current_user.find_facebook_contact(friend['id'])
                if not contact:
                    contact = FacebookContact()
                    contact.name = friend['name']
                    contact.facebook_id = friend['id']
                    contact.user = current_user
                    session.add(contact)
                else:
                    contact.name = friend['name']

        return redirect(url_for('contacts'))

    except GraphAPI.OAuthError:
        return redirect(create_facebook_authorize_url(
            action_url=url_for('import_facebook_friends'),
            error_url=url_for('contacts')
        ))


@app.route('/connect/facebook/done')
@login_required
def facebook_connected():
    action_url = request.args['action_url']
    error_url = request.args['error_url']

    try:
        code = request.args.get('code', None)
        if not code:
            raise GraphAPI.OAuthError('No code parameter found in request arguments.')

        oauth2_handler = create_facebook_oauth_handler('https://graph.facebook.com/', action_url, error_url)
        response = oauth2_handler.get_token(code)
        if not response or 'access_token' not in response:
            raise GraphAPI.OAuthError('No access token returned from Facebook.')

        session['facebook_access_token'] = response['access_token']
        return redirect(action_url)

    except GraphAPI.OAuthError:
        flash('Facebook connection has failed.')
        return redirect(error_url)

