# -*- coding: utf-8 -*-


from flask import render_template
from oleander import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sign-up/')
def sign_up():
    return 'Registration'


@app.route('/sign-in/')
def sign_in():
    return 'Login'