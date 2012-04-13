# -*- coding: utf-8 -*-


import re
from setuptools import setup


# version handling
def find_version():
    version_file = 'oleander/__init__.py'
    try:
        match = re.search(r'__version__ = [\'"]([^\'"]*)[\'"]', open(version_file, 'r').read())
    except IOError:
        raise RuntimeError("Unable to find version string in '%s'." % version_file)
    if match:
        return match.group(1)
    else:
        raise RuntimeError("Unable to find version string in '%s'." % version_file)


setup(
    name = 'oleander',
    version = find_version(),
    description = 'Library for agnostic communitation between people.',
    url = 'https://github.com/honzajavorek/oleander',
    author = 'Honza Javorek',
    author_email = 'honza@javorek.net',
    license = 'MIT',
    packages = ['oleander', 'tests']
)

