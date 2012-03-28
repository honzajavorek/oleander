# -*- coding: utf-8 -*-


from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object('oleander.default_settings')
app.config.from_envvar('OLEANDER_SETTINGS', silent=True)


import oleander.views
