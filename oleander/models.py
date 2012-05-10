# -*- coding: utf-8 -*-


from flask.ext.login import UserMixin
from oleander import app, db
from random import choice
import hashlib
import string
import operator
import sqlalchemy
import datetime
import times


class GravatarMixin(object):
    """Support for gravatar."""

    @property
    def avatar(self):
        # see https://secure.gravatar.com/site/implement/images
        return 'https://secure.gravatar.com/avatar/%s?s=50&d=mm' % hashlib.md5(self.email).hexdigest()


class User(db.Model, UserMixin, GravatarMixin):
    """User model class."""

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column('name', db.String(100), nullable=False)
    password_hash = db.Column(db.String(40), nullable=False)
    password_salt = db.Column(db.String(10), nullable=False)
    timezone = db.Column(db.String(100), nullable=False, default=app.config['DEFAULT_TIMEZONE'])

    def _get_contact(self, type):
        try:
            return self.contacts.filter(Contact.type == type)\
                .filter(Contact.belongs_to_user == True)\
                .order_by(db.desc(Contact.is_primary))\
                .first()
        except sqlalchemy.orm.exc.DetachedInstanceError:
            return None

    def _set_contact(self, type, field_name, field_value, as_primary=False):
        # no fun when name is missing
        if not self.name:
            raise ValueError("Can't create dependent contacts without name.")

        cls = _contact_type_factory(type)
        try:
            contact = cls.query.filter(cls.belongs_to_user == True)\
                .filter(cls.user == self)\
                .filter(cls.type == type)\
                .filter_by(**{field_name: field_value})\
                .first()
        except sqlalchemy.orm.exc.DetachedInstanceError:
            contact = None

        if not contact:
            contact = cls()
            contact.type = type
            contact.user = self
            setattr(contact, field_name, field_value)

        contact.name = self.name
        contact.belongs_to_user = True

        if as_primary:
            contact.set_as_primary()

    @property
    def email(self):
        return getattr(self._get_contact('email'), 'email', None)

    @email.setter
    def email(self, value):
        self._set_contact('email', field_name='email', field_value=value)

    @property
    def primary_email(self):
        return self.email

    @primary_email.setter
    def primary_email(self, value):
        self._set_contact('email', field_name='email', field_value=value, as_primary=True)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        try:
            Contact.query.with_polymorphic(Contact)\
                .filter(Contact.belongs_to_user == True)\
                .filter(Contact.user == self)\
                .update({Contact.name: value})
        except sqlalchemy.orm.exc.DetachedInstanceError:
            pass

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

    def event_or_404(self, id):
        """Returns user's event by given ID or aborts the request."""
        return self.events.filter(Event.id == id).first_or_404()

    @property
    def events_active(self):
        return self.events\
            .filter(Event.cancelled_at == None)\
            .order_by(db.desc(Event.updated_at))

    @property
    def events_upcoming(self):
        return self.events\
            .filter(Event.starts_at > times.now())\
            .filter(Event.cancelled_at == None)\
            .order_by(db.desc(Event.starts_at))

    @property
    def events_current(self):
        now = times.now()
        return self.events\
            .filter(Event.starts_at < now)\
            .filter(Event.ends_at > now)\
            .filter(Event.cancelled_at == None)\
            .order_by(Event.starts_at)

    @property
    def events_past(self):
        return self.events\
            .filter(Event.starts_at < times.now())\
            .filter(Event.cancelled_at == None)\
            .order_by(Event.starts_at)

    @property
    def events_cancelled(self):
        return self.events\
            .filter(Event.cancelled_at != None)\
            .order_by(db.desc(Event.cancelled_at))

    def delete_contact(self, id):
        Contact.query.with_polymorphic(Contact)\
            .filter(Contact.id == id)\
            .filter(Contact.user == self)\
            .filter(Contact.is_primary == False)\
            .delete()

    @classmethod
    def fetch_by_email(self, email):
        contact = Contact.query.filter(
                db.or_(
                    EmailContact.email == email,
                    GoogleContact.email == email
                )
            )\
            .filter(Contact.belongs_to_user == True)\
            .first()
        return contact.user

    def __repr__(self):
        return '<User %r (%r)>' % (self.name, self.email)


def _contact_type_factory(type):
    if type == 'email':
        return EmailContact
    if type == 'google':
        return GoogleContact
    if type == 'facebook':
        return FacebookContact
    raise TypeError("No contact type associated with '%s'." % type)


def create_contact(type):
    cls = _contact_type_factory(type)
    return cls()


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


class DeletedContact(ContactMixin):
    """Contact representing a previously deleted one."""

    def __init__(self, type, name, identifier, avatar=None):
        self.type = type
        self.name = name
        self.identifier = identifier
        self.avatar = avatar or None


class Contact(db.Model, ContactMixin):
    """Base contact model class."""

    contact_types = {
        'email': u'E-mail',
        'facebook': u'Facebook',
        'google': u'Google',
    }

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(*contact_types.keys(), name='contact_types'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', backref=db.backref('contacts', cascade='all', lazy='dynamic'))
    belongs_to_user = db.Column(db.Boolean(), nullable=False, default=False)
    is_primary = db.Column(db.Boolean(), nullable=False, default=False)
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

    def set_as_primary(self):
        primary_contact = Contact.query\
            .filter(Contact.user_id == self.user_id)\
            .filter(Contact.is_primary == True)\
            .first()
        if primary_contact:
            primary_contact.is_primary = False
        self.is_primary = True

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
    type = db.Column(db.Enum(*['going', 'maybe', 'declined', 'invited'], name='attendance_types'), nullable=False)

    def __repr__(self):
        return '<Attendance %r @ %r (%s)>' % (self.contact, self.event, self.type)


class Event(db.Model):
    """Event."""

    default_end_time_offset = 2 # in hours

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text())
    venue = db.Column(db.String(200))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    user = db.relationship('User', backref=db.backref('events', cascade='all', lazy='dynamic'))
    attendance = db.relationship('Attendance')
    created_at = db.Column(db.DateTime(), nullable=False, default=lambda: times.now())
    updated_at = db.Column(db.DateTime(), nullable=False, default=lambda: times.now(), onupdate=lambda: times.now())
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
        if not att:
            att = Attendance(contact=contact, event=self)
            att.type = type
            db.session.add(att)
        else:
            att.type = type

    @property
    def contacts(self):
        return Contact.query.join(Attendance).filter(Attendance.event_id == self.id)

    @property
    def contacts_invited(self):
        return self.contacts.filter(Attendance.type == 'invited')

    @contacts_invited.setter
    def contacts_invited(self, contacts):
        for contact in contacts:
            self.set_attendance(contact, 'invited')

    @property
    def contacts_invited_ids_str(self):
        return ','.join([c.id for c in self.contacts_invited])

    @contacts_invited_ids_str.setter
    def contacts_invited_ids_str(self, ids_str):
        ids = set(filter(None, ids_str.split(',')))
        self.contacts_invited = list(Contact.query.filter(Contact.id.in_(ids)))

    @property
    def contacts_going(self):
        return self.contacts.filter(Attendance.type == 'going')

    @property
    def contacts_maybe(self):
        return self.contacts.filter(Attendance.type == 'maybe')

    @property
    def contacts_declined(self):
        return self.contacts.filter(Attendance.type == 'declined')

    @property
    def is_cancelled(self):
        return self.cancelled_at is not None

    @property
    def ends_at(self):
        if self._ends_at:
            return self._ends_at
        if self.starts_at:
            return (
                self.starts_at + datetime.timedelta(hours=self.default_end_time_offset)
            )
        return None

    @ends_at.setter
    def ends_at(self, value):
        self._ends_at = value

    def _are_valid_coords(self, lat, lng):
        return lat is not None and lng is not None

    @property
    def verbose_name(self):
        verbose_name = self.name
        if self.is_cancelled:
            verbose_name += ' (cancelled)'
        return verbose_name

    @classmethod
    def fetch_or_404(self, id):
        """Returns event by given ID or aborts the request."""
        return Event.query.filter(Event.id == id).first_or_404()

    def __repr__(self):
        return '<Event %r>' % self.name
