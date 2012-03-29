# -*- coding: utf-8 -*-


from flask import render_template
from flask.ext.login import login_required
from oleander import app, db
from oleander.forms import EmailContactForm
from oleander.models import Contact


@app.route('/contacts/', methods=('GET', 'POST'))
@login_required
def contacts():
    """Contacts management page."""
    form = EmailContactForm()

    if form.validate_on_submit():
        with db.transaction as session:
            contact = Contact()
            form.populate_obj(contact)
            session.add(contact)
        return redirect(url_for('contacts'))

    return render_template('contacts.html', form=form)


