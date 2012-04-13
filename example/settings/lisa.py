# -*- coding: utf-8 -*-
# settings file for Lisa, my development machine


DEBUG = True
SECRET_KEY = '\xc1\xef\x81uET\x08B\x90w\xa5t\n\xe5SD\x117FpoP-\x0f'


SQLALCHEMY_DATABASE_URI = 'postgresql://dev:dev@localhost/oleander'


MAIL_SERVER = 'smtp.sendgrid.net'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'honzajavorek'
MAIL_PASSWORD = 'vnzp00y'.decode('rot13')


MAIL_SERVER_RECEIVING = 'mail.honzajavorek.cz'

