# -*- coding: utf-8 -*-


from flask import abort, request, render_template
from oleander import app
from functools import wraps
import re


_re_normalize_whitespace = re.compile('\\s+')


def ajax_only(fn):
    """Decorator forcing the view to be AJAX-only. Ignored on debug."""
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not request.is_xhr and not app.debug:
            abort(405) # method not allowed
        return fn(*args, **kwargs)
    return decorated_view


def template_to_html(template, **kwargs):
    html = render_template(template, **kwargs)
    return _re_normalize_whitespace.sub(' ', html.strip())