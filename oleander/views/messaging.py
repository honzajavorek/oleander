# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.models import Topic
from oleander.forms import TopicForm
import times


@app.route('/group/<int:group_id>/topics/new', methods=('GET', 'POST'))
@login_required
def new_topic(group_id):
    """Form to create a new discussion topic."""
    group = current_user.group_or_404(group_id)
    form = TopicForm()
    now = times.now()

    if form.validate_on_submit():
        with db.transaction as session:
            topic = Topic()
            form.populate_obj(topic)
            topic.group = group
            topic.created_at = now
            topic.updated_at = now
            session.add(topic)
        return redirect(url_for('topic', id=topic.id, group_id=group.id))

    return render_template('new_topic.html', group=group, form=form, now=times.now())


@app.route('/group/<int:group_id>/topic/<int:id>', methods=('GET', 'POST'))
@login_required
def topic(id, group_id):
    """Form to create a new discussion topic."""
    pass