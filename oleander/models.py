# -*- coding: utf-8 -*-


from oleander import app, db, login_manager
from flask.ext.login import UserMixin
from pytz import common_timezones
import hashlib
import uuid
import times


@login_manager.user_loader
def load_user(user_id):
    """User loader used by sign-in process."""
    return User.query.filter_by(id=user_id).first()


def tz_choices():
    choices = []
    for tz in common_timezones:
        places = tz.split('/')
        places.reverse()
        label = ', '.join(places).replace('_', ' ')
        time = times.format(times.now(), tz, '%H:%M')
        choices.append((tz, time + u' – ' + label))

    return sorted(choices, key=lambda choice: choice[1])


class User(db.Model, UserMixin):
    """User model class."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(40))
    password_salt = db.Column(db.String(36))
    timezone = db.Column(db.String(100), default=app.config['DEFAULT_TIMEZONE'])

    def set_password(self, password):
        """New password setter."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')

        salt = str(uuid.uuid4())
        hash = hashlib.sha1(password + salt).hexdigest()

        self.password_hash = hash
        self.password_salt = salt

    password = property(fset=set_password)

    def check_password(self, password):
        """Checks if given password is the same as the one in database."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')

        hash = hashlib.sha1(password + self.password_salt).hexdigest()
        return hash == self.password_hash
