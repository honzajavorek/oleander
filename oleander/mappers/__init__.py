# -*- coding: utf-8 -*-


class Mapper(object):
    """Base mapper class."""

    def __init__(self, entity_class=None):
        self.entity_class = entity_class or dict

    def create_entity(self, **kwargs):
        """Creates a new entity."""
        return self.entity_class(**kwargs)
