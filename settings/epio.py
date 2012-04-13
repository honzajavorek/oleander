# -*- coding: utf-8 -*-
# settings file for ep.io, production cloud service


from bundle_config import config


DEBUG = False
SECRET_KEY = 'c\xeb\xca\xa4%<1\x08\xd4\x93\x95!\xbe\xd7\x19`\xdc\x13\xaa\x18\x8a?\xbe>'


SQLALCHEMY_DATABASE_URI = 'postgresql://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s' % config['postgres']


MAIL_SERVER = 'smtp.sendgrid.net'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'honzajavorek'
MAIL_PASSWORD = '************'


MAIL_SERVER_RECEIVING = 'mail.honzajavorek.cz'

