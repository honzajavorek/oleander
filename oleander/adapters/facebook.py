# -*- coding: utf-8 -*-


from oleander.adapters import DependencyError
from oleander import Entity
from datetime import datetime


try:
    from facepy import GraphAPI
except ImportError:
    raise DependencyError("Facebook adapter requires 'facepy' (github.com/jgorset/facepy).")


class FacebookContactMapper(object):

    def _parse_date(self, date_string):
        try:
            parsed_datetime = datetime.strptime(date_string, '%d/%m/%Y')
            return parsed_datetime.date()
        except ValueError:
            return None

    def source_to_contact(self, contact):
        """Map Facebook user info into contact entities."""
        locale = contact.get('locale', None)
        language = locale[:2] if locale else None

        bday_date = self._parse_date(contact.get('birthday', ''))

        location_obj = contact.get('location', contact.get('hometown', None))
        location = location_obj['name'] if location_obj else None

        # map values to contact object
        return Entity(
            name=contact.get('name', None),
            first_name=contact.get('first_name', None),
            middle_name=contact.get('middle_name', None),
            last_name=contact.get('last_name', None),
            gender=contact.get('gender', None),
            birthday=bday_date,
            location=location,
            language=language,
            website=contact.get('website', contact.get('link', None)),
            email=contact.get('email', None),
            facebook_id=contact.get('id', None),
            facebook_username=contact.get('username', None),
        )


class FacebookAdapter(object):
    """Adapter for Facebook Graph API."""

    def __init__(self, oauth_access_token):
        self.graph = GraphAPI(oauth_access_token)

    @property
    def contacts(self):
        contacts = []
        mapper = FacebookContactMapper()

        friends = self.graph.get('me/friends').get('data', [])
        for friend in friends:
            friend_id = friend.get('id', None)
            if friend_id:
                contacts.append(mapper.source_to_contact(self.graph.get(friend_id)))
        return contacts

