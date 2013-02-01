# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
"""Tests for event related actions."""
from __future__ import with_statement

from StringIO import StringIO
import os

from jinja2 import DictLoader, Environment
from mock import patch

from chevah.utils import MODULE_PATH
from chevah.utils.testing import (
    LogTestCase,
    manufacture,
    UtilsTestCase,
    )
from chevah.utils.constants import (
    CONFIGURATION_ALL_LOG_ENABLED_GROUPS,
    )
from chevah.utils.event import (
    Event,
    EventDefinition,
    EventGroupDefinition,
    EventsDefinition,
    EventsHandler,
    )
from chevah.utils.exceptions import (
    UtilsError,
    )
from chevah.utils.interfaces import (
    IEvent,
    IEventDefinition,
    IEventGroupDefinition,
    IEventsDefinition,
    )


class TestEventGroupDefinition(UtilsTestCase):
    """Unit tests for EventGroupDefinition."""

    def test_init(self):
        """
        Check EventGroupDefinition initialization.
        """
        name = manufacture.getUniqueString()
        description = manufacture.getUniqueString()

        event_group = EventGroupDefinition(
            name=name, description=description)

        self.assertProvides(IEventGroupDefinition, event_group)
        self.assertEqual(name, event_group.name)
        self.assertEqual(description, event_group.description)


class TestEventDefinition(UtilsTestCase):
    """
    Unit tests for EventDefinition.
    """

    def test_init(self):
        """
        Check EventDefinition initialization.
        """
        event_id = manufacture.getUniqueString() + 'greater_than_5'
        description = manufacture.getUniqueString()
        message = manufacture.getUniqueString()
        version_added = manufacture.getUniqueString()
        version_removed = manufacture.getUniqueString()
        groups = [
            manufacture.makeEventGroupDefinition(),
            manufacture.makeEventGroupDefinition(),
            ]

        event_definition = EventDefinition(
            id=event_id,
            message=message,
            description=description,
            groups=groups,
            version_added=version_added,
            version_removed=version_removed,
            )

        self.assertProvides(IEventDefinition, event_definition)
        self.assertEqual(event_id, event_definition.id)
        self.assertEqual(message, event_definition.message)
        self.assertEqual(groups, event_definition.groups)
        self.assertEqual(description, event_definition.description)
        self.assertEqual(version_added, event_definition.version_added)
        self.assertEqual(version_removed, event_definition.version_removed)
        self.assertEqual(
            [groups[0].name, groups[1].name], event_definition.group_names)

    def test_eventID_padding(self):
        """
        Id's less than 5 characters in length will be padded with 0 at the
        start.
        """
        event_id = '20'

        event_definition = EventDefinition(
            id=event_id,
            message=u'don-t care',
            )

        self.assertEqual('20', event_definition.id)
        self.assertEqual('00020', event_definition.id_padded)

        event_id = '100320'

        event_definition = EventDefinition(
            id=event_id,
            message=u'don-t care',
            )

        self.assertEqual('100320', event_definition.id)
        self.assertEqual('100320', event_definition.id_padded)


class TestEvent(UtilsTestCase):
    """Unit tests for Event."""

    def test_init(self):
        """
        Check Event initialization.
        """
        event_id = manufacture.getUniqueString()
        message = manufacture.getUniqueString()
        data = {
            'attr1': 'value1',
            'attr2': 'value2',
            'peer': manufacture.makeIPv4Address(),
            'avatar': manufacture.makeFilesystemApplicationAvatar()}

        event = Event(
            id=event_id,
            message=message,
            data=data,
            )

        self.assertProvides(IEvent, event)
        self.assertEqual(event_id, event.id)
        self.assertEqual(message, event.message)
        self.assertEqual(data, event.data)


class TestEventsDefinition(UtilsTestCase):
    """
    Unit tests for EventsDefinition.
    """

    def test_init(self):
        """
        Check object initialization.
        """
        events_file = StringIO()

        definitions = EventsDefinition(file=events_file)

        self.assertProvides(IEventsDefinition, definitions)

    def test_load_default_events_file(self):
        """
        Check that the events file is valid.
        """
        path = os.path.join(
            MODULE_PATH, 'static', 'events', 'events.json')
        definitions = EventsDefinition(path=path)

        definitions.load()

        self.assertIsNotEmpty(definitions.getAllEventDefinitions())
        self.assertIsNotEmpty(definitions.getAllEventGroupDefinitions())

    def test_load_bad_config_file(self):
        """
        Trying to configure from a bad formated configuration file
        will raise UtilsError.
        """
        content = manufacture.getUniqueString()
        definitions = manufacture.makeEventsDefinition(
            content=content, load=False)

        with self.assertRaises(UtilsError) as context:
            definitions.load()

        self.assertExceptionID(u'1028', context.exception)

    def test_load_empty(self):
        """
        An EventGroup with just a complex or simple description will load
        just fine.
        """
        definitions = manufacture.makeEventsDefinition(content=u'')

        definitions.load()

        self.assertIsEmpty(definitions.getAllEventDefinitions())
        self.assertIsEmpty(definitions.getAllEventGroupDefinitions())

    def test_load_EventGroup_good(self):
        """
        An EventGroup with just a complex or simple description will load
        just fine.
        """
        name_1 = manufacture.getUniqueString()
        name_2 = manufacture.getUniqueString()
        description = manufacture.getUniqueString()
        content = '''
            {
            "groups" : {
                "%s": { "description": "%s"},
                "%s": { "description": ""}
                },
            "events" : {}
            }
            ''' % (name_1, description, name_2)
        definitions = manufacture.makeEventsDefinition(content=content)

        group = definitions.getEventGroupDefinition(name=name_1)
        self.assertEqual(name_1, group.name)
        self.assertEqual(description, group.description)
        group = definitions.getEventGroupDefinition(name=name_2)
        self.assertEqual(name_2, group.name)

    def test_load_EventDefinition_good(self):
        """
        An EventDefinition with a message and groups will load just fine.
        """
        event_id = manufacture.getUniqueString()
        group_1 = manufacture.getUniqueString()
        group_2 = manufacture.getUniqueString()
        message = manufacture.getUniqueString()
        content = '''
            {
            "groups" : {
                "%s": { "description": ""},
                "%s": { "description": ""}
                },
            "events" : {
                "%s": {
                    "message": "%s",
                    "groups": ["%s", "%s"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            ''' % (group_1, group_2, event_id, message, group_1, group_2)
        config = manufacture.makeEventsDefinition(
            content=content, load=False)

        config.load()

        event_definition = config.getEventDefinition(id=event_id)

        self.assertEqual(event_id, event_definition.id)
        self.assertEqual(message, event_definition.message)
        self.assertEqual(2, len(event_definition.groups))
        self.assertIsNone(event_definition.version_added)
        self.assertIsNone(event_definition.version_removed)
        self.assertIsNone(event_definition.description)

    def test_load_EventDefinition_missing_group(self):
        """
        Loading an EventDefinition with a reference to a non-existent group
        will raise UtilsError.
        """
        event_id = manufacture.getUniqueString()
        group_1 = manufacture.getUniqueString()
        message = manufacture.getUniqueString()
        content = '''
            {
            "groups" : {},
            "events" : {
                "%s": {
                    "message": "%s",
                    "groups": ["%s"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            ''' % (event_id, message, group_1)
        config = manufacture.makeEventsDefinition(
            content=content, load=False)

        with self.assertRaises(UtilsError):
            config.load()

    def test_getAllEventGroupDefinitions_good(self):
        """
        An getAllEventGroupDefinitions with return a dictionary with all
        defined EventGroups.
        """
        name_1 = manufacture.getUniqueString()
        name_2 = manufacture.getUniqueString()
        description = manufacture.getUniqueString()
        content = '''
            {
            "groups" : {
                "%s": { "description": "%s"},
                "%s": { "description": ""}
                },
            "events" : {}
            }
            ''' % (name_1, description, name_2)
        config = manufacture.makeEventsDefinition(content=content)

        result = config.getAllEventGroupDefinitions()

        self.assertEqual(2, len(result))
        self.assertTrue(name_1 in result)
        self.assertTrue(name_2 in result)

    def test_getAllEventDefinitions_good(self):
        """
        An getAllEventDefinitions with return a dictionary with all
        defined EventDefinitons keyed by event id.
        """
        content = '''
            {
            "groups" : {
                "group-1": { "description": ""}
                },
            "events" : {
                "ev1": {
                    "message": "something",
                    "groups": ["group-1"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    },
                "ev2": {
                    "message": "something",
                    "groups": ["group-1"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        config = manufacture.makeEventsDefinition(content=content)

        result = config.getAllEventDefinitions()

        self.assertEqual(2, len(result))
        self.assertTrue(u'ev1' in result)
        self.assertTrue(u'ev2' in result)

    def test_getAllEventDefinitionsPadded(self):
        """
        An test_getAllEventDefinitionsPadded with return a dictionary with all
        defined EventDefinitons keyed by padded event id.
        """
        content = '''
            {
            "groups" : {
                "group-1": { "description": ""}
                },
            "events" : {
                "ev1": {
                    "message": "something",
                    "groups": ["group-1"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    },
                "event3": {
                    "message": "something",
                    "groups": ["group-1"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        config = manufacture.makeEventsDefinition(content=content)

        result = config.getAllEventDefinitionsPadded()

        self.assertTrue(u'00ev1' in result)
        self.assertTrue(u'event3' in result)

    def test_generateDocumentation_good(self):
        """
        The handler can generates a RESTructuredText file documenting
        the events and event groups.
        """
        content = '''
            {
            "groups" : {
                "group-1": { "description": ""},
                "group-2": { "description": ""}
                },
            "events" : {
                "ev1": {
                    "message": "something",
                    "groups": ["group-1", "group-2"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    },
                "ev2": {
                    "message": "something",
                    "groups": ["group-1"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    },
                "event3": {
                    "message": "something",
                    "groups": ["group-2"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        template_content = (
            'Header\n'
            '=======\n'
            '{% for group_id in groups %}\n'
            '{{ groups[group_id].name }}\n'
            '----\n'
            'description: {{ groups[group_id].description }}\n'
            '\n'
            '{% endfor %}\n'
            '\n'
            '{% for event_id in events %}\n'
            '{{ events[event_id].id }}\n'
            '----\n'
            'message: {{ events[event_id].message }}\n'
            'groups: {{ ", ".join(events[event_id].group_names) }}\n'
            '\n'
            '{% endfor %}\n'
            )
        config = manufacture.makeEventsDefinition(content=content)
        templates_loader = DictLoader(
            {'events_documentation.rst': template_content})
        jinja_environment = Environment(loader=templates_loader)
        template = jinja_environment.get_template('events_documentation.rst')

        result = config.generateDocumentation(template=template)

        self.assertTrue('ev1' in result)
        self.assertTrue('groups: group-1, group-2' in result)


class TestEventsHandler(LogTestCase):
    """
    Unit tests for EventsHandler.
    """

    def test_init(self):
        """
        EventsHandler can be initialized without arguments.
        """
        handler = EventsHandler()

        self.assertFalse(handler.configured)

        with self.assertRaises(AssertionError):
            handler.definitions

        with self.assertRaises(AssertionError):
            handler.enabled_groups

    def test_configure(self):
        """
        EventsHandler can be configured.
        """
        handler = EventsHandler()
        definitions = manufacture.makeEventsDefinition()
        log_configuration_section = manufacture.makeLogConfigurationSection()

        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)

        self.assertTrue(handler.configured)
        self.assertIsNotNone(handler.definitions)
        self.assertEqual(
            [CONFIGURATION_ALL_LOG_ENABLED_GROUPS], handler.enabled_groups)

    def test_removeConfiguration(self):
        """
        EventsHandler configurations can be removed using removeConfiguration.
        """
        handler = EventsHandler()
        definitions = manufacture.makeEventsDefinition()
        log_configuration_section = manufacture.makeLogConfigurationSection()
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)
        self.assertTrue(handler.configured)

        handler.removeConfiguration()

        self.assertFalse(handler.configured)

    def test_emit_without_configuration(self):
        """
        If handler is not configured, all events will be logged using only
        data from the event.
        Event definitions and other configurations is not used.
        """
        handler = EventsHandler()
        message = u'Some message ' + manufacture.getUniqueString()

        handler.emit('100', message=message)

        self.assertLog(100, regex=u'Some ')

    def test_log(self):
        """
        `log` method is here for transition and used the old Logger.log
        interface to emit an event.
        """
        handler = EventsHandler()
        message = u'Some message ' + manufacture.getUniqueString()
        peer = manufacture.makeIPv4Address()
        avatar = manufacture.makeFilesystemApplicationAvatar()
        data = {}
        handler.log(100, message, peer=peer, avatar=avatar, data=data)

        log_message = self.popLog()
        self.assertEqual(100, log_message[0])
        self.assertTrue('Some message' in log_message[1])
        self.assertEqual(avatar, log_message[2])
        self.assertEqual(peer, log_message[3])
        self.assertEqual(data, log_message[4])

    def test_emit_with_int_id(self):
        """
        When event id is an integer, it will be converted to string.
        """
        handler = EventsHandler()
        message = u'Some message ' + manufacture.getUniqueString()

        with patch.object(handler, 'emitEvent') as patched:
            handler.emit(100, message=message)

        event = patched.call_args[0][0]
        self.assertEqual(u'100', event.id)

    def test_emit_with_unicode_id(self):
        """
        Events can be emitted with unicode ids.
        """
        handler = EventsHandler()
        message = u'Some message ' + manufacture.getUniqueString()

        with patch.object(handler, 'emitEvent') as patched:
            handler.emit(u'100', message=message)

        event = patched.call_args[0][0]
        self.assertEqual(u'100', event.id)

    def test_emit_with_string_id(self):
        """
        Events can be emitted with string ids and are converted to unicode.
        """
        handler = EventsHandler()
        message = u'Some message ' + manufacture.getUniqueString()

        with patch.object(handler, 'emitEvent') as patched:
            handler.emit(u'100', message=message)

        event = patched.call_args[0][0]
        self.assertEqual(u'100', event.id)

    def test_emit_unknown_id(self):
        """
        Emitting an event with unknown ID will log an error containing
        the text of the unknown id.
        """
        handler = EventsHandler()
        message = u'Some message ' + manufacture.getUniqueString()
        definitions = manufacture.makeEventsDefinition()
        log_configuration_section = manufacture.makeLogConfigurationSection()
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section,
            )

        handler.emit(u'100', message=message)

        self.assertLog(
            1024, regex='Unknown event with id "100"')

    def test_emit_with_configuration(self):
        """
        If handler is configured, the logs can be filterd.
        """
        handler = EventsHandler()
        content = '''
            {
            "groups" : {
                "enabled": { "description": ""},
                "disabled": { "description": ""}
                },
            "events" : {
                "100": {
                    "message": "some message",
                    "groups": ["enabled"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    },
                "101": {
                    "message": "other message",
                    "groups": ["disabled"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        definitions = manufacture.makeEventsDefinition(content=content)
        log_configuration_section = manufacture.makeLogConfigurationSection()
        log_configuration_section.enabled_groups = ['enabled']
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)

        handler.emit('101', message='101some message')
        handler.emit('100', message='100some message')

        self.assertLog(100, regex="100some m")

    def test_emit_with_all(self):
        """
        When 'all' group is enabled, logs will be enabled even if their
        groups is not explicitly enabled.
        """
        handler = EventsHandler()
        content = '''
            {
            "groups" : {
                "disabled": { "description": ""}
                },
            "events" : {
                "100": {
                    "message": "some message",
                    "groups": ["disabled"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    },
                "101": {
                    "message": "other message",
                    "groups": ["disabled"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        definitions = manufacture.makeEventsDefinition(content=content)
        log_configuration_section = manufacture.makeLogConfigurationSection()
        log_configuration_section.enabled_groups = [
            CONFIGURATION_ALL_LOG_ENABLED_GROUPS]
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)

        handler.emit('101', message='101some message')
        handler.emit('100', message='100some message')

        self.assertLog(101, regex="101some m")
        self.assertLog(100, regex="100some m")

    def test_emit_message_from_definition_no_data(self):
        """
        If not message was defined for emit, the message from event definition
        will be used.

        When no data is provided the string will not be interpolated.
        """
        handler = EventsHandler()
        content = '''
            {
            "groups" : {
                "group": { "description": "something"}
                },
            "events" : {
                "100": {
                    "message": "100 %(replace)s some message",
                    "groups": ["group"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        definitions = manufacture.makeEventsDefinition(content=content)
        log_configuration_section = manufacture.makeLogConfigurationSection()
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)

        handler.emit('100', data={'replace': 'test'})

        self.assertLog(100, regex="100 test some m")

    def test_emit_message_from_definition_with_data(self):
        """
        When data is provided the message will be interpolated based on
        data and event_definition.
        """
        handler = EventsHandler()
        content = '''
            {
            "groups" : {
                "group": { "description": "something"}
                },
            "events" : {
                "100": {
                    "message": "100 %(data)s some message",
                    "groups": ["group"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        definitions = manufacture.makeEventsDefinition(content=content)
        log_configuration_section = manufacture.makeLogConfigurationSection()
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)

        data_string = manufacture.getUniqueString()
        handler.emit('100', data={'data': data_string})

        self.assertLog(100, regex="100 " + data_string + " some m")

    def test_emit_message_from_definition_bad_interpolation(self):
        """
        When wrong data is provided the an additional message is logged
        together with the non-interpolated message.
        """
        handler = EventsHandler()
        content = '''
            {
            "groups" : {
                "group": { "description": "something"}
                },
            "events" : {
                "100": {
                    "message": "100 %(unknown_data)s some message",
                    "groups": ["group"],
                    "description": "",
                    "version_removed": "",
                    "version_added": "",
                    "details": "",
                    "data": ""
                    }
                }
            }
            '''
        definitions = manufacture.makeEventsDefinition(content=content)
        log_configuration_section = manufacture.makeLogConfigurationSection()
        handler.configure(
            definitions=definitions,
            log_configuration_section=log_configuration_section)

        handler.emit('100', data={'other': u'dontcare'})

        self.assertLog(1025)
        self.assertLog(100, regex='100 %\(unknown_data\)s some message')
