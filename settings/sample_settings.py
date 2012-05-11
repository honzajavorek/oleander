# -*- coding: utf-8 -*-
# sample settings file


DEBUG = False
SECRET_KEY = 'see http://flask.pocoo.org/docs/quickstart/#sessions'


SQLALCHEMY_DATABASE_URI = 'sqlite:///'


MAIL_SERVER = 'smtp.sendgrid.net'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = '********'


FACEBOOK_APP_ID = '145571488891413'
FACEBOOK_APP_SECRET = '**************'
FACEBOOK_SCOPE = ''