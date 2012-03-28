# -*- coding: utf-8 -*-


from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('oleander.default_settings')
app.config.from_envvar('OLEANDER_SETTINGS', silent=True)


db = SQLAlchemy(app)


import oleander.views
import oleander.models