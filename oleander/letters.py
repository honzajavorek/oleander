# -*- coding: utf-8 -*-


from oleander import app
from itertools import groupby as _groupby
from jinja2.filters import _GroupTuple
from operator import itemgetter
import codecs
import string



codecs.register_error(
        'alphabetical_directory',
        lambda error: (u'#', error.start + 1)
    )


class Letter(str):
    """Alphabet letter. Implements comparing where '#' is at the end of alhpabet."""

    def __lt__(self, other):
        if self == '#':
            return False
        if other == '#':
            return True
        return str(self) < other

    def __le__(self, other):
        if self == '#':
            return False
        if other == '#':
            return True
        return str(self) <= other

    def __gt__(self, other):
        if self == '#':
            return True
        if other == '#':
            return False
        return str(self) > other

    def __ge__(self, other):
        if self == '#':
            return True
        if other == '#':
            return False
        return str(self) >= other

    def __repr__(self):
        return '<Letter %s>' % str(self)

    @property
    def name(self):
        if self == '#':
            return 'hash'
        return str(self).lower()


def alphabet():
    """Generates an alphabet letters. Character '#' is the last one, representing all non-ASCII letters."""
    return map(Letter, string.ascii_uppercase)


def first_letter(str):
    """Returns uppercase first letter or '#' in case it's not ASCII letter."""
    return Letter(str[:1].upper().encode('ascii', 'alphabetical_directory'))


@app.template_filter('groupby_alphabet')
def groupby(value, attribute, full_alphabet=False):
    """Group alphabetically a sequence of objects by a common attribute."""
    attr_getter = lambda item: first_letter(getattr(item, attribute))
    grouped = _groupby(sorted(value, key=attr_getter), attr_getter)

    if full_alphabet:
        # convert grouped to dict
        grouped = dict(map(lambda group: (group[0], list(group[1])), grouped))

        # prepare unique set of all used and alphabetic letters
        all_letters = sorted(set(grouped.keys() + list(alphabet())))

        # return special tuples, empty list is used if there are no items
        # for given letter
        return [_GroupTuple(
            (letter, grouped.get(letter, []))
        ) for letter in all_letters]

    return sorted(map(_GroupTuple, grouped))

