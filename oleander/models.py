# -*- coding: utf-8 -*-


#from flask import current_app as app
from flask.ext.login import UserMixin
from oleander import app, db
from random import choice
import hashlib
import string
import operator


class GravatarMixin(object):
    """Support for gravatar."""

    @property
    def avatar(self):
        # see https://secure.gravatar.com/site/implement/images
        return 'https://secure.gravatar.com/avatar/%s?s=50&d=mm' % hashlib.md5(self.email).hexdigest()


class User(db.Model, UserMixin, GravatarMixin):
    """User model class."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(40), nullable=False)
    password_salt = db.Column(db.String(10), nullable=False)
    timezone = db.Column(db.String(100), nullable=False, default=app.config['DEFAULT_TIMEZONE'])

    def _generate_salt(self, length=10, chars=string.letters + string.digits):
        """Generates random alphanumeric string of specified length."""
        return ''.join([choice(chars) for i in range(length)])

    def set_password(self, password):
        """New password setter."""
        if isinstance(password, unicode):
            password = password.encode('utf-8')

        salt = self._generate_salt()
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
        return by_name.union(by_email, by_id_or_username).order_by(Contact.name).limit(limit)

    @property
    def current_topics(self):
        """Returns user's current topics."""
        return Topic.query\
            .join(Group)\
            .filter(Group.user == self)\
            .order_by(db.desc(Topic.updated_at))

    @property
    def contact_types(self):
        return ['email']

    def group_or_404(self, id):
        """Returns user's group by given ID or aborts the request."""
        return self.groups.filter(Group.id == id).first_or_404()

    def topic_or_404(self, id, group_id=None):
        """Returns user's topic by given IDs or aborts the request."""
        query = Topic.query\
            .join(Group)\
            .filter(Group.user == self)\
            .filter(Topic.id == id)
        if group_id:
            query = query.filter(Group.id == group_id)
        return query.first_or_404()


class ContactMixin(object):
    """Mixin for all contacts."""

    type = None
    name = None
    avatar = None
    identifier = None

    @property
    def label(self):
        return Contact.contact_types[self.type]

    def __eq__(self, other):
        return self.identifier == getattr(other, 'identifier', None)

    def __hash__(self):
        return hash(self.identifier)


class UserContact(ContactMixin):
    """Contact created from User instance."""

    def __init__(self, type, user):
        self.type = type
        self.name = user.name
        self.avatar = user.avatar
        self.user = user

        if type == 'email':
            self.identifier = user.email
        else:
            raise NotImplementedError("Type '%s' is not supported yet" % type)


class DeletedContact(ContactMixin):
    """Contact representing a previously deleted one."""

    def __init__(self, type, name, identifier, avatar=None):
        self.type = type
        self.name = name
        self.identifier = identifier
        self.avatar = avatar or None



class Contact(db.Model, ContactMixin):
    """Base contact model class."""

    contact_types = {'email': u'E-mail', 'facebook': u'Facebook', 'google': u'Google'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(*contact_types.keys(), name='contact_types'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', backref=db.backref('contacts', cascade='all', lazy='dynamic'))

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


class EmailContact(GravatarMixin, Contact):
    """Simple contact represented by a plain e-mail address."""

    slug = 'email'

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

    def contacts_by_type(self, type):
        return filter(lambda contact: contact.type == type, self.contacts)

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

    @property
    def members(self):
        contacts = list(self.contacts)
        for type in self.user.contact_types:
            contacts.append(
                UserContact(type, self.user)
            )
        return sorted(contacts, key=lambda c: c.name)

    def member_by_identifier(self, identifier):
        for contact in self.members:
            if contact.identifier == identifier:
                return contact
        return None


class Topic(db.Model):
    """Discussion topic."""

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    group_id = db.Column(db.Integer(), db.ForeignKey('group.id', ondelete='cascade'), nullable=False)
    group = db.relationship('Group', backref=db.backref('topics', cascade='all', lazy='dynamic'))
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)
    _hash = db.Column('hash', db.String(32), nullable=True)

    __mapper_args__ = {
        'order_by': db.desc(updated_at),
    }

    @property
    def contacts(self):
        return sorted(list(set(message.contact for message in self.messages)), key=lambda c: c.name)

    def generate_hash(self):
        if self.subject is None or self.id is None:
            raise ValueError('Missing topic subject or ID.')
        id = str(self.id)
        salt = self.subject.encode('utf-8')
        self._hash = hashlib.md5(id + '/' + salt).hexdigest()

    @property
    def hash(self):
        if not self._hash:
            self.generate_hash()
        return self._hash


class TopicModel(object):
    """Topic model."""

    def get_by_hash(hash, or_404=False):
        query = Topic.query.filter(Topic._hash == hash)
        if or_404:
            return query.first_or_404()
        return query.first()


class Message(db.Model):
    """Message in topic."""

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer(), db.ForeignKey('topic.id', ondelete='cascade'), nullable=False)
    topic = db.relationship('Topic', backref=db.backref('messages', cascade='all', lazy='dynamic'))
    _user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    _user = db.relationship('User', backref=db.backref('messages', cascade='all', lazy='dynamic'))
    _contact_id = db.Column('contact_id', db.Integer(), db.ForeignKey('contact.id', ondelete='cascade'), nullable=True)
    _contact_name = db.Column('contact_name', db.String(200), nullable=False)
    _contact_identifier = db.Column('contact_identifier', db.String(200), nullable=False)
    _contact_avatar = db.Column('contact_avatar', db.String(500), nullable=False)
    _contact = db.relationship('Contact', backref=db.backref('messages', cascade='all', lazy='dynamic'))
    type = db.Column(db.Enum(*Contact.contact_types, name='contact_types'))
    content = db.Column(db.Text(), nullable=False)
    posted_at = db.Column(db.DateTime(), nullable=False)

    __mapper_args__ = {
        'order_by': posted_at,
    }

    @property
    def contact(self):
        if self._user_id or self._contact_id:
            return UserContact(self.type, self._user) or self._contact

        # contact doesn't exist anymore
        return DeletedContact(
            self.type,
            self._contact_name,
            self._contact_identifier,
            self._contact_avatar
        )

        return None

    @contact.setter
    def contact(self, contact):
        self._user = getattr(contact, 'user', None)
        self._contact = contact if hasattr(contact, 'id') else None

        if contact is None:
            self.type = None
            self._contact_name = None
            self._contact_identifier = None
            self._contact_avatar = None
        else:
            self.type = contact.type
            self._contact_name = contact.name
            self._contact_identifier = contact.identifier
            self._contact_avatar = contact.avatar
