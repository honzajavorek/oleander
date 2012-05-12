# -*- coding: utf-8 -*-


from flask import url_for, request, session
from oleander import app
from gdata.gauth import OAuth2Token, Error as OAuthError, token_to_blob, token_from_blob
from gdata.contacts.client import ContactsClient
from gdata.calendar.client import CalendarClient


# https://developers.google.com/gdata/faq#AuthScopes
# http://googleappsdeveloper.blogspot.com/2011/09/python-oauth-20-google-data-apis.html
# http://stackoverflow.com/questions/10188768/google-contacts-import-using-oauth2-0


ConnectionError = OAuthError


def create_oauth_handler(scope=''):
    oauth2_handler = OAuth2Token(
        client_id=app.config['GOOGLE_APP_ID'],
        client_secret=app.config['GOOGLE_APP_SECRET'],
        scope=scope,
        user_agent=''
    )
    web_hook_url = url_for(
        'google_connected',
        _external=True
    )
    oauth2_handler.generate_authorize_url(
        redirect_uri=web_hook_url
    )
    return oauth2_handler


def create_authorize_url(action_url, error_url, scope=''):
    oauth2_handler = create_oauth_handler(scope)
    session['action_url'] = action_url
    session['error_url'] = error_url
    return oauth2_handler.generate_authorize_url(
        redirect_uri=oauth_callback
    )


def create_api(cls):
    credentials = session.get('google_credentials', None)
    if not credentials:
        raise ConnectionError('No credentials.')
    credentials = token_from_blob(credentials)
    client = cls(source='') # source - user agent
    credentials.authorize(client)
    return client
