# -*- coding: utf-8 -*-


from oleander import app
from flask.ext.login import current_user
from jinja2 import Markup
import re
import times


@app.template_filter('mark')
def mark(s, term, pattern=r'%(term)'):
    """Marks a term by a <mark> tag. Useful for search results."""
    re_marking = re.compile(pattern % dict(term=re.escape(term)), re.I)
    return Markup(re_marking.sub(r'<mark>\g<0></mark>', unicode(Markup.escape(s))))


@app.template_filter('datetime')
def datetime(dt):
    """Formats datetime objects."""
    # TODO dynamic datetime formatting (see how Gmail does it)
    return times.format(dt, current_user.timezone or app.config['DEFAULT_TIMEZONE'], '%H:%M')


from oleander.letters import groupby as groupby_alphabet

