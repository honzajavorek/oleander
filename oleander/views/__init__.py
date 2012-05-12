# -*- coding: utf-8 -*-


modules = [
    'auth',
    'contacts',
    'events',
    'settings',
    'facebook',
    'google',
]


__all__ = modules


for module in modules:
    name = '.'.join([__name__, module])
    __import__(name)

