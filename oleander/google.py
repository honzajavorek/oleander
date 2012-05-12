# -*- coding: utf-8 -*-


from flask import url_for, request, session
from oleander import app
from oauth2client.client import OAuth2WebServerFlow, FlowExchangeError
from oauth2client.tools import run


# https://developers.google.com/gdata/faq#AuthScopes


ConnectionError = FlowExchangeError


def create_oauth_handler(scope=''):
    return OAuth2WebServerFlow(
        app.config['GOOGLE_APP_ID'],
        app.config['GOOGLE_APP_SECRET'],
        scope
    )


def create_authorize_url(action_url, error_url, scope=''):
    oauth2_handler = create_oauth_handler(scope)
    oauth_callback = url_for(
        'google_connected',
        action_url=action_url,
        error_url=error_url,
        _external=True
    )
    return oauth2_handler.step1_get_authorize_url(oauth_callback)


def create_api(type, action_url, error_url, scope=''):
    credentials = session.get('google_credentials', None)
    if credentials is None or credentials.invalid:
        raise ConnectionError('No credentials.')
    http = httplib2.Http()
    credentials.authorize(http)
    return build(type, 'v3', http=http)
