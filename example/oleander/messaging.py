# -*- coding: utf-8 -*-


from flask.ext.mail import Mail, Message as _EmailMessage
from oleander import app


class EmailMessage(_EmailMessage):
    """Adds support for reply_to."""

    def __init__(self, *args, **kwargs):
        if 'reply_to' in kwargs:
            self.reply_to = kwargs['reply_to']
            del kwargs['reply_to']
        super(EmailMessage, self).__init__(*args, **kwargs)

    def get_response(self):
        response = super(EmailMessage, self).get_response()
        if self.reply_to:
            response.base['Reply-To'] = self.reply_to
        return response


def _send_email(message):
    topic = message.topic
    recipients = [('%s <%s>' % (contact.name, contact.identifier)) for contact in topic.group.contacts_by_type('email')]
    reply_to_email = '@'.join([topic.hash, app.config['MAIL_SERVER_RECEIVING']])

    subject = topic.subject
    body = message.content
    sender = '%s <%s>' % (message.contact.name, message.contact.identifier)
    reply_to = '%s <%s>' % (message.contact.name, reply_to_email)

    mail = Mail(app)
    with mail.connect() as conn:
        for recipient in recipients:
            conn.send(
                EmailMessage(subject, recipients=[recipient], body=body, sender=sender, reply_to=reply_to)
            )


def send(message):
    if message.type == 'email':
        _send_email(message)
    else:
        raise NotImplementedError("Message type '%s' is not supported." % message.type)
