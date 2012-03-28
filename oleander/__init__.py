# -*- coding: utf-8 -*-


from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from oleander.database import Transaction


app = Flask(__name__)
app.config.from_object('oleander.default_settings')
app.config.from_envvar('OLEANDER_SETTINGS', silent=True)


db = SQLAlchemy(app)
db.transaction = Transaction(db)


import oleander.views
