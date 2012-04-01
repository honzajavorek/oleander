# -*- coding: utf-8 -*-


from oleander import app, db
from flask.ext.login import UserMixin
from random import choice
import hashlib
import string
import operator


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

    def search_contacts(self, term, limit=5):
        """Searches contacts by a given term."""
        pattern = term + '%'

        # basic name search
        by_name = self.contacts.filter(Contact.name.ilike(pattern))

        # by special attributes
        by_email = self.contacts.filter(db.or_(EmailContact.email.ilike(pattern), GoogleContact.email.ilike(pattern)))
        by_id_or_username = self.contacts.filter(db.or_(db.cast(FacebookContact.user_id, db.String).ilike(pattern), FacebookContact.username.ilike(pattern)))

        # union of results
        return by_name.union(by_email, by_id_or_username).limit(limit)


class Contact(db.Model):
    """Base contact model class."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column('type', db.Enum(*['email', 'facebook', 'google'], name='contact_types'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', backref=db.backref('contacts', cascade='all', lazy='dynamic'))
    identifier = None
    avatar = None

    __mapper_args__ = {
        'polymorphic_on': type,
        'with_polymorphic': '*',
    }

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    def to_dict(self):
        return dict(
            id=self.id,
            name=self.name,
            type=self.type,
            identifier=self.identifier,
            avatar=self.avatar
        )


class GravatarMixin(object):
    """Support for gravatar."""

    @property
    def avatar(self):
        # see https://secure.gravatar.com/site/implement/images
        return 'https://secure.gravatar.com/avatar/%s?s=50&d=mm' % hashlib.md5(self.email).hexdigest()


class EmailContact(GravatarMixin, Contact):
    """Simple contact represented by a plain e-mail address."""

    slug = 'email'
    label = u'E-mail'

    id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)

    __tablename__ = 'contact_' + slug

    __mapper_args__ = {
        'polymorphic_identity': slug,
    }

    @property
    def identifier(self):
        return self.email


class FacebookContact(Contact):
    """Facebook contact represented by a Facebook account."""

    slug = 'facebook'
    label = u'Facebook'

    id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=True)

    __tablename__ = 'contact_' + slug

    __mapper_args__ = {
        'polymorphic_identity': slug,
    }

    @property
    def identifier(self):
        return 'facebook.com/' + (self.username or self.user_id)

    @property
    def avatar(self):
        return 'https://graph.facebook.com/%s/picture?type=square' % self.user_id


class GoogleContact(GravatarMixin, Contact):
    """Google contact represented by a Gmail and/or Google+ account."""

    slug = 'google'
    label = u'Google'

    id = db.Column(db.Integer, db.ForeignKey('contact.id', ondelete='cascade'), primary_key=True)
    email = db.Column(db.String(100), nullable=False)

    __tablename__ = 'contact_' + slug

    __mapper_args__ = {
        'polymorphic_identity': slug,
    }

    @property
    def identifier(self):
        return self.email


grouping = db.Table('grouping',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id')),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id'))
)


class Group(db.Model):
    """Group of contacts."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', backref=db.backref('groups', cascade='all', lazy='dynamic'))
    contacts = db.relationship('Contact', secondary=grouping, backref=db.backref('groups', lazy='dynamic'))

    __mapper_args__ = {
        'order_by': name,
    }

    @property
    def contact_ids(self):
        return [contact.id for contact in self.contacts]

    @contact_ids.setter
    def contact_ids(self, ids):
        self.contacts = list(Contact.query.filter(Contact.id.in_(ids)))

    @property
    def contact_ids_str(self):
        return ','.join(map(str, self.contact_ids))

    @contact_ids_str.setter
    def contact_ids_str(self, ids_str):
        ids = map(int, set(filter(None, ids_str.split(','))))
        self.contact_ids = ids
