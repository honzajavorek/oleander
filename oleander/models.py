# -*- coding: utf-8 -*-


from flask.ext.login import UserMixin
from oleander import app, db
from random import choice
import hashlib
import string
import operator
from datetime import timedelta


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
    def contact_types(self):
        return ['email']

    def event_or_404(self, id):
        """Returns user's event by given ID or aborts the request."""
        return self.events.filter(Event.id == id).first_or_404()

    def __repr__(self):
        return '<User %r (%r)>' % (self.name, self.email)


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
    attendance = db.relationship('Attendance')

    __mapper_args__ = {
        'polymorphic_on': type,
        'with_polymorphic': '*',
    }

    def set_attendance(self, event, type):
        att = Attendance.query.filter(Attendance.contact_id == self.id)\
            .filter(Attendance.event_id == event.id)\
            .first()
        att = att or Attendance(contact=self, event=event)
        att.type = type

    def __repr__(self):
        return '<%s %r (%r)>' % (self.__class__.__name__, self.name, self.identifier)

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


class Attendance(db.Model):
    """Attendance of contacts to events."""

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    event = db.relationship('Event')
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), primary_key=True)
    contact = db.relationship('Contact')
    type = db.Column(db.Enum(*['yes', 'maybe', 'no'], name='attendance_types'), nullable=False)


class Venue(object):
    """Simple data container representing an event's venue."""

    def __init__(self, name=None, lat=None, lng=None):
        self.name = name
        self.lat = lat
        self.lng = lng

    @property
    def coords(self):
        return (self.lat, self.lng)

    @coords.setter
    def coords(self, value):
        self.lat, self.lng = value

    def to_dict(self):
        return dict(
            name=self.name,
            lat=self.lat,
            lng=self.lng
        )

    def __repr__():
        return '<Venue %r (%r;%r)>' % (self.name, self.lat, self.lng)


class Event(db.Model):
    """Event."""

    default_end_time_offset = 2 # in hours

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text())
    _venue_name = db.Column('venue_name', db.String(200))
    _venue_lat = db.Column('venue_lat', db.Float())
    _venue_lng = db.Column('venue_lng', db.Float())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', cascade='all', lazy='dynamic'))
    attendance = db.relationship('Attendance')
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)
    cancelled_at = db.Column(db.DateTime())
    starts_at = db.Column(db.DateTime())
    _ends_at = db.Column('ends_at', db.DateTime())

    __mapper_args__ = {
        'order_by': db.desc(created_at),
    }

    def set_attendance(self, contact, type):
        att = Attendance.query.filter(Attendance.contact_id == contact.id)\
            .filter(Attendance.event_id == self.id)\
            .first()
        att = att or Attendance(contact=contact, event=self)
        att.type = type

    @property
    def contacts(self):
        return Contact.query.join(Attendance).filter(Attendance.event_id == self.id)

    @property
    def contacts_yes(self):
        return self.contacts.filter(Attendance.type == 'yes')

    @property
    def contacts_maybe(self):
        return self.contacts.filter(Attendance.type == 'maybe')

    @property
    def contacts_no(self):
        return self.contacts.filter(Attendance.type == 'no')

    @property
    def is_cancelled(self):
        return self.cancelled_at is not None

    @property
    def ends_at(self):
        if self._ends_at:
            return self._ends_at
        if self.starts_at:
            return (
                self.starts_at + timedelta(hours=self.default_end_time_offset)
            )
        return None

    @ends_at.setter
    def ends_at(self, value):
        self._ends_at = value

    def _are_valid_coords(self, lat, lng):
        return lat is not None and lng is not None

    @property
    def venue(self):
        has_name = self._venue_name
        has_valid_coords = self._are_valid_coords(self._venue_lat, self._venue_lng)

        if has_name or has_valid_coords:
            venue = Venue()
            if has_name:
                venue.name = self._venue_name
            if has_valid_coords:
                venue.lat = self._venue_lat
                venue.lng = self._venue_lng
            return venue
        return None

    @venue.setter
    def venue(self, value):
        if value.name:
            self._venue_name = value.name
        if self._are_valid_coords(value.lat, value.lng):
            self._venue_lat = value.lat
            self._venue_lng = value.lng

    @classmethod
    def fetch_or_404(self, id):
        """Returns event by given ID or aborts the request."""
        return Event.query.filter(Event.id == id).first_or_404()

    def __repr__(self):
        return '<Event %r>' % self.name
