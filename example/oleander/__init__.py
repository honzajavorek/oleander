# -*- coding: utf-8 -*-


from flask import Flask
from oleander.database import create_db


app = Flask('oleander')
app.config.from_object('oleander.default_settings')
app.config.from_envvar('OLEANDER_SETTINGS', silent=False)

db = create_db(app=app)

import oleander.models
import oleander.views
import oleander.templating
