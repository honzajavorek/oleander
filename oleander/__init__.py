# -*- coding: utf-8 -*-


__version__ = '0.0.1'


class Oleander(object):
    """Main controller for agnostic communitation with services."""

    def __init__(self):
        self._adapters = {}

    def register_adapter(self, service_name, adapter):
        """Register service adapter."""
        self._adapters[service_name] = adapter

    def __class_from_string(self, import_string):
        """Take import string and return corresponding class object."""
        components = import_string.split('.')
        module_name = '.'.join(components[:-1])
        class_name = components[-1]
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)

    def _adapter_for_service(self, service_name):
        """Return adapter for given service name. If registered as string, import it first."""
        try:
            adapter = self._adapters[service_name]
        except KeyError:
            raise LookupError("There is no adapter registered for a service named '%s'." % service_name)

        if isinstance(adapter, basestring):
            # adapter registered by import string, such as 'awesome_module.adapters.GargamelAdapter'
            cls = self.__class_from_string(adapter)
            adapter = cls()
            self._adapters[service_name] = adapter
        return adapter

    def __getattr__(self, service_name):
        return self._adapter_for_service(service_name)


class Entity(object):
    """Simple & benevolent data container."""

    def __init__(self, **properties):
        self.__dict__.update(properties)

    def __getattr__(self, property):
        return None
