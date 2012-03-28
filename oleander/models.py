# -*- coding: utf-8 -*-


from oleander import db
import hashlib
import os


class User(db.Model):
    """User model class."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(40))
    password_salt = db.Column(db.String(20))
    timezone = db.Column(db.String(100))

    def set_password(self, password):
        """New password setter."""
        salt = os.urandom(20)
        hash = hashlib.sha1(password + salt).hexdigest()

        self.password_hash = hash
        self.password_salt = salt

    password = property(fset=set_password)

    def check_password(self, password):
        """Checks if given password is the same as the one in database."""
        hash = hashlib.sha1(password + self.password_salt).hexdigest()
        return hash == self.password_hash
