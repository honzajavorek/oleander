# -*- coding: utf-8 -*-


from oleander import app, db
from flask.ext.login import UserMixin
from random import choice
import hashlib
import string


def salt_generator(length=10, chars=string.letters + string.digits):
    """Generates random alphanumeric string of specified length."""
    return ''.join([choice(chars) for i in range(length)])


class User(db.Model, UserMixin):
    """User model class."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(40), nullable=False)
    password_salt = db.Column(db.String(10), nullable=False)
    timezone = db.Column(db.String(100), nullable=False, default=app.config['DEFAULT_TIMEZONE'])

    def set_password(self, password):
        """New password setter."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')

        salt = salt_generator()
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


class Contact(db.Model):
    """Base contact model class."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column('type', db.Enum(*['email', 'facebook', 'google'], name='contact_types'), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': type,
        'with_polymorphic': '*',
    }


class EmailContact(Contact):
    """Simple contact represented by a plain e-mail address."""

    slug = 'email'

    id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)

    __tablename__ = 'contact_' + slug

    __mapper_args__ = {
        'polymorphic_identity': slug,
    }


class FacebookContact(Contact):
    """Facebook contact represented by a Facebook account."""

    slug = 'facebook'

    id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=True)

    __tablename__ = 'contact_' + slug

    __mapper_args__ = {
        'polymorphic_identity': slug,
    }


class GoogleContact(Contact):
    """Google contact represented by a Gmail and/or Google+ account."""

    slug = 'google'

    id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)

    __tablename__ = 'contact_' + slug

    __mapper_args__ = {
        'polymorphic_identity': slug,
    }

