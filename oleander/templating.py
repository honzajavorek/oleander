# -*- coding: utf-8 -*-


from oleander import app
from flask.ext.login import current_user
from jinja2 import Markup
import re
import urllib2
import times


@app.template_filter('mark')
def mark(s, term, pattern=r'%(term)'):
    """Marks a term by a <mark> tag. Useful for search results."""
    re_marking = re.compile(pattern % dict(term=re.escape(term)), re.I)
    return Markup(re_marking.sub(r'<mark>\g<0></mark>', unicode(Markup.escape(s))))


@app.template_filter('datetime')
def datetime(dt):
    """Formats datetime objects."""
    return times.format(dt, getattr(current_user, 'timezone', app.config['DEFAULT_TIMEZONE']), '%x, %H:%M')


@app.template_filter('map_link')
def map_link(place_name):
    """Returns URL to maps."""
    return 'https://maps.google.com/maps?q=' + urllib2.quote(place_name)


from oleander.letters import groupby as groupby_alphabet

