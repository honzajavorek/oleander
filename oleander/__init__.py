# -*- coding: utf-8 -*-


__version__ = '0.0.1'


class Oleander(object):

    def __init__(self):
        self._mappers = {}
        self._adapters = {}

    def register_mapper(self, entity_name, mapper):
        self._mappers[entity_name] = mapper

    def register_adapter(self, service_name, adapter):
        self._adapters[service_name] = adapter

    def _class_from_string(self, import_string):
        components = import_string.split('.')
        module_name = '.'.join(components[:-1])
        class_name = components[-1]
        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)

    def _mapper_for_entity(self, entity_name):
        try:
            mapper = self._mappers[entity]
        except KeyError:
            raise ValueError("There is no mapper registered for an entity named '%s'." % entity)\

        if isinstance(mapper, basestring):
            # mapper registered by import string, such as 'awesome_module.mappers.SmurfMapper'
            cls = self._class_from_string(mapper)
            mapper = cls()
            self._mappers[entity] = mapper
        return mapper

    def _adapter_for_service(self, service_name):
        try:
            adapter = self._adapters[service]
        except KeyError:
            raise ValueError("There is no adapter registered for a service named '%s'." % service)

        if isinstance(adapter, basestring):
            # adapter registered by import string, such as 'awesome_module.adapters.GargamelAdapter'
            cls = self._class_from_string(adapter)
            adapter = cls()
            self._adapters[service] = adapter
        return adapter

    def _format_mapper_method(self, action, service_name):
        if action == 'get':
            return 'from_' + service_name
        elif action == 'send':
            return 'to_' + service_name
        else:
            raise ValueError("Unknown action %s." % action)

    def _format_adaper_method(self, action, entity_name):
        if action in ('get', 'send'):
            return action + '_' + entity_name
        else:
            raise ValueError("Unknown action %s." % action)

    def _call_mapper(self, mapper, action, service_name, data=None):
        method_name = self._format_mapper_method(action, service_name)
        if hasattr(mapper, method_name):
            method = getattr(mapper, method_name)
            return method() if data is None else method(data)
        else:
            class_name = mapper.__class__.__name__
            raise NotImplementedError(
                "Mapper '%s' can't map '%s' request for service '%s'." % (class_name, action, service_name)
            )

    def _call_adapter(self, adapter, action, entity_name, data=None):
        method_name = self._format_adapter_method(action, entity_name)
        if hasattr(adapter, method_name):
            method = getattr(adapter, method_name)
            return method() if data is None else method(data)
        else:
            class_name = adapter.__class__.__name__
            raise NotImplementedError(
                "Adapter '%s' can't %s entities of type '%s'." % (class_name, action, entity_name)
            )

    def get(entity_name, service_name):
        mapper = self._mapper_for_entity(entity_name)
        adapter = self._adapter_for_service(service_name)

        response = self._call_adapter(adapter, 'get', entity_name)
        return self._call_mapper(mapper, 'get', service_name, data=response)

    def send(entity_name, service_name, data=None):
        mapper = self._mapper_for_entity(entity_name)
        adapter = self._adapter_for_service(service_name)

        service_friendly_data = self._call_mapper(mapper, 'send', service_name, data=data)
        response = self._call_adapter(adapter, 'send', entity_name, data=service_friendly_data)
        return self._call_mapper(mapper, 'get', service_name, data=response)

