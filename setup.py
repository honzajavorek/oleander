# -*- coding: utf-8 -*-


import re
import oleander
from setuptools import setup


setup(
    name = 'oleander',
    version = oleander.__version__,
    description = 'Library for agnostic communitation between people.',
    long_description=open('README').read(),
    url = 'https://github.com/honzajavorek/oleander',
    author = 'Honza Javorek',
    author_email = 'honza@javorek.net',
    license = open('LICENSE').read(),
    packages = ['oleander', 'tests']
)

