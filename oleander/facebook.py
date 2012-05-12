# -*- coding: utf-8 -*-


from flask import url_for, request, session
from oleander import app
from oauth2 import OAuth2
from facepy import GraphAPI


ConnectionError = GraphAPI.OAuthError


def create_oauth_handler(site, action_url, error_url):
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


def create_authorize_url(action_url, error_url, scope=''):
    oauth2_handler = create_oauth_handler('https://www.facebook.com/', action_url, error_url)
    return oauth2_handler.authorize_url(scope)


def create_api():
    access_token = session.get('facebook_access_token', None)
    if not access_token:
        raise ConnectionError('No access token.')
    return GraphAPI(access_token)