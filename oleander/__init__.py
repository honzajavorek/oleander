# -*- coding: utf-8 -*-


from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

from oleander.database import Transaction


app = Flask(__name__)
app.config.from_object('oleander.default_settings')
app.config.from_envvar('OLEANDER_SETTINGS', silent=True)


db = SQLAlchemy(app)
db.transaction = Transaction(db)


login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'sign_in'
login_manager.needs_refresh = 'sign_in'


import oleander.views
