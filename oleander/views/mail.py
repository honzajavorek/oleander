# -*- coding: utf-8 -*-


from flask import request, json
from oleander import app, db
from oleander.models import Message, TopicModel
from oleander.messaging import send
from bs4 import BeautifulSoup
import re
import times


class SendGridEmailParser(object):

    _default_encoding = 'utf-8'

    def __init__(self, data):
        self._data = data
        self._charsets = json.loads(data.get('charsets', {}))

    def __getattr__(self, name):
        name = name.rstrip('_')
        if name in self._data:
            charset = self._charsets.get(name, self._default_encoding)
            return str(self._data[name]).decode(charset)
        return None

    def _remove_tags(html):
        return ''.join(BeautifulSoup(page).find_all(text=True))

    def _parse_email(email):
        """Returns e-mail address. Accepts 'Honza <honza@example.com>' or 'honza@example.com'."""
        match = re.search(r'[^<]+@[^>]+')
        if match:
            return match.group(0).strip()
        return None

    @property
    def plaintext_body():
        return self.text or self._remove_tags(email_parser.html)

    def get_as_email(name):
        return self._parse_email(getattr(self, name))


@app.route('/mail', methods=('POST',))
def mail():
    """Sendgrid Parse API endpoint."""
    # On error sends HTTP 200, because SendGrid tries to send the mail
    # again and again in case it receives 4xx or 5xx status codes

    # parse the mail
    send_grid = SendGridEmailParser(request.form)
    email_from = send_grid.get_as_email('from') # sender's e-mail address
    email_to = send_grid.get_as_email('to') # topic_hash@our_mailserver.domain
    email_body = send_grid.plaintext_body

    # find the topic, check validity of destination
    topic_hash, mailserver = email_to.split('@')
    if mailserver != app.config['MAIL_SERVER_RECEIVING']:
        return "FAIL: Invalid mailserver '%s'." % mailserver

    topic = TopicModel().get_by_hash(topic_hash)
    if topic is None:
        return "FAIL: Invalid topic hash '%s'." % topic_hash

    # verify sender is allowed to post into this topic
    contact = topic.member_by_identifier(email_from)
    if contact is None:
        return "FAIL: Sender '%s' is not allowed to post into topic '%s'." % (email_from, topic_hash)

    # finally, save the message
    now = times.now()
    with db.transaction as session:
        message = Message()
        message.content = email_body
        message.topic = topic
        message.posted_at = now
        message.contact = contact
        session.add(message)

        topic.updated_at = now

        send(message)

    return 'OK'