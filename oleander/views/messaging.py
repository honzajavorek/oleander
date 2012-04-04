# -*- coding: utf-8 -*-


from flask import render_template, redirect, url_for
from flask.ext.login import login_required, current_user
from oleander import app, db
from oleander.models import Topic, Message, UserContact
from oleander.forms import TopicForm, MessageForm
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
            topic.subject = form.subject.data
            topic.group = group
            topic.created_at = now
            topic.updated_at = now
            session.add(topic)

            message = Message()
            message.content = form.message.data
            message.topic = topic
            message.posted_at = now
            message.contact = UserContact('email', current_user)
            session.add(message)

        return redirect(
            url_for('topic', id=topic.id, group_id=topic.group_id)\
            + '#message-%d' % message.id
        )

    return render_template('new_topic.html', group=group, form=form, now=now)


@app.route('/group/<int:group_id>/topic/<int:id>', methods=('GET', 'POST'))
@login_required
def topic(id, group_id):
    """Form to create a new discussion topic."""
    topic = current_user.topic_or_404(id, group_id=group_id)
    form = MessageForm()
    now = times.now()

    if form.validate_on_submit():
        with db.transaction as session:
            message = Message()
            message.content = form.message.data
            message.topic = topic
            message.posted_at = now
            message.contact = UserContact('email', current_user)
            session.add(message)

            topic.updated_at = now

        return redirect(
            url_for('topic', id=topic.id, group_id=topic.group_id)\
            + '#message-%d' % message.id
        )

    return render_template('topic.html', topic=topic, form=form, now=now)