# -*- coding: utf-8 -*-


__all__ = [
    'auth',
    'contacts',
    'groups',
    'index',
    'settings',
]


for module in __all__:
    name = '.'.join([__name__, module])
    __import__(name)