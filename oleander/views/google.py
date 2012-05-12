# -*- coding: utf-8 -*-


from flask import session, request, flash, redirect
from oleander import app, google
from flask.ext.login import login_required


@app.route('/connect/google/done')
@login_required
def google_connected():
    action_url = request.args['action_url']
    error_url = request.args['error_url']

    try:
        code = request.args.get('code', None)
        if not code:
            raise google.ConnectionError('No code parameter found in request arguments.')

        oauth2_handler = google.create_oauth_handler()
        credentials = oauth2_handler.step2_exchange(code, http)
        session['google_credentials'] = credentials
        return redirect(action_url)

    except google.ConnectionError:
        flash('Google connection has failed.')
        return redirect(error_url)