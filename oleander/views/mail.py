# -*- coding: utf-8 -*-


from flask import request
from oleander import app


@app.route('/mail', methods=('POST',))
def mail():
    """Sendgrid Parse API endpoint."""
    print request.form
    return 'OK'