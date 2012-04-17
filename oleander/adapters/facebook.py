# -*- coding: utf-8 -*-


try:
    from facepy import GraphAPI
except ImportError:
    raise DependencyError("Facebook adapter needs 'facepy' library. Type `pip install facepy` to install or visit https://github.com/jgorset/facepy.")


