# -*- coding: utf-8 -*-


from flask import session, request, flash, redirect
from oleander import app, facebook
from flask.ext.login import login_required


@app.route('/connect/facebook/done')
@login_required
def facebook_connected():
    action_url = request.args['action_url']
    error_url = request.args['error_url']

    try:
        code = request.args.get('code', None)
        if not code:
            raise facebook.OAuthError('No code parameter found in request arguments.')

        oauth2_handler = facebook.create_oauth_handler('https://graph.facebook.com/', action_url, error_url)
        response = oauth2_handler.get_token(code)
        if not response or 'access_token' not in response:
            raise facebook.OAuthError('No access token returned from Facebook.')

        session['facebook_access_token'] = response['access_token']
        return redirect(action_url)

    except facebook.OAuthError:
        flash('Facebook connection has failed.')
        return redirect(error_url)