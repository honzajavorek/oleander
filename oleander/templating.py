# -*- coding: utf-8 -*-


from oleander import app
from jinja2 import Markup
import re


@app.template_filter('mark')
def mark(s, term, pattern=r'%(term)'):
    """Marks a term by a <mark> tag. Useful for search results."""
    re_marking = re.compile(pattern % dict(term=re.escape(term)), re.I)
    return Markup(re_marking.sub(r'<mark>\g<0></mark>', unicode(Markup.escape(s))))


from oleander.letters import groupby as groupby_alphabet

