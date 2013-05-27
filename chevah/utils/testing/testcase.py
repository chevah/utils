# -*- coding: utf-8 -*-
# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''TestCase factories for Chevah server.'''
from collections import deque
import re
import json

from chevah.empirical.testcase import ChevahTestCase
from chevah.utils.constants import (
    CONFIGURATION_DISABLED_VALUES,
    CONFIGURATION_INHERIT,
    )

from chevah.utils.logger import Logger
from chevah.utils import events_handler


class UtilsTestCase(ChevahTestCase):
    """
    Test case for Chevah tests.

     * provides support for running deferred and start/stop the reactor.
     * checks that temporary folder is clean at exit
    """

    def defaultBoolean(self, option):
        '''Return default boolean value.'''
        _boolean_states = {'1': True, 'yes': True, 'true': True,
                                      'on': True,
                           '0': False, 'no': False, 'false': False,
                                       'off': False}
        return _boolean_states[
            self.CONFIGURATION_DEFAULTS[option].lower()]

    def defaultString(self, option):
        '''Return default boolean value.'''
        return self.CONFIGURATION_DEFAULTS[option]

    def defaultStringOrNone(self, option):
        '''Return default boolean value.'''
        value = self.CONFIGURATION_DEFAULTS[option]
        if value in CONFIGURATION_DISABLED_VALUES:
            return None

    def defaultInteger(self, option):
        '''Return default boolean value.'''
        return int(self.CONFIGURATION_DEFAULTS[option])

    def assertPropertyString(self, config_factory, key):
        """
        Helper for string properties.
        """
        raw_config = u'%s: something_ță\n' % (key)
        config = config_factory(raw_config=raw_config)

        option = getattr(config, key)
        self.assertEqual(u'something_ță', option)

        setattr(config, key, u'else_ță')
        option = getattr(config, key)
        self.assertEqual(u'else_ță', option)

    def _checkPropertyStringInherit(self, config_factory, key):
        """
        Helper for checking inherit values for a string.
        """
        raw_config = u'%s: Inherit\n' % (key)
        config = config_factory(raw_config=raw_config)

        option = getattr(config, key).lower()
        self.assertEqual(CONFIGURATION_INHERIT[0], option)

        # Setting sinonim for Inherit, will return Inherit base value.
        setattr(config, key, CONFIGURATION_INHERIT[1])

        option = getattr(config, key).lower()
        self.assertEqual(CONFIGURATION_INHERIT[0], option)

    def assertPropertyStringInherit(self, config_factory, key):
        """
        Helper for testing string properties which can be inherited.
        """
        self.assertPropertyString(config_factory=config_factory, key=key)
        self._checkPropertyStringInherit(
            config_factory=config_factory, key=key)

    def _checkPropertyStringNone(self, config_factory, key):
        """
        Helper for checking None values for a string.
        """
        value = {}
        value[key] = 'Disabled'
        config = config_factory(value=value)
        option = getattr(config, key)
        self.assertIsNone(option)

        setattr(config, key, None)
        option = getattr(config, key)
        self.assertIsNone(option)

        setattr(config, key, u'Disabled')
        option = getattr(config, key)
        self.assertIsNone(option)

    def assertPropertyStringOrNone(self, config_factory, key):
        """
        Helper for string properties which can be None.
        """
        self.assertPropertyString(config_factory=config_factory, key=key)
        self._checkPropertyStringNone(config_factory=config_factory, key=key)

    def assertPropertyStringSpecial(self, config_factory, key):
        """
        Helper for string properties which can have special values.
        """
        self.assertPropertyString(config_factory=config_factory, key=key)
        self._checkPropertyStringNone(config_factory=config_factory, key=key)
        self._checkPropertyStringInherit(
            config_factory=config_factory, key=key)

    def assertPropertyBoolean(self, config_factory, key):
        """
        Helper for testing boolean properties.
        """
        raw_config = u'%s: False\n' % (key)
        config = config_factory(raw_config=raw_config)

        option = getattr(config, key)
        self.assertFalse(option)

        setattr(config, key, True)

        option = getattr(config, key)
        self.assertIsTrue(option)

        setattr(config, key, False)

        option = getattr(config, key)
        self.assertIsFalse(option)

    def assertPropertyBooleanInherit(self, config_factory, key):
        """
        Helper for testing boolean properties which can be inherited.
        """
        raw_config = u'%s: Inherit\n' % (key)
        config = config_factory(raw_config=raw_config)

        option = getattr(config, key).lower()
        self.assertEqual(CONFIGURATION_INHERIT[0], option)

        setattr(config, key, True)

        option = getattr(config, key)
        self.assertIsTrue(option)

        setattr(config, key, False)

        option = getattr(config, key)
        self.assertIsFalse(option)

        setattr(config, key, 'Inherit')

        option = getattr(config, key).lower()
        self.assertEqual(CONFIGURATION_INHERIT[0], option)


class EventTestCase(UtilsTestCase):
    """
    A test case which checks that all emited events are tested.
    """

    def setUp(self):
        """
        Catch all emited events.
        """
        super(EventTestCase, self).setUp()

        def emitEvent_test(event):
            """
            Push the logging message into the log testing queue.
            """
            self._queue.append(event)

        self._queue = deque([])
        self.emitEvent_good = events_handler.emitEvent
        events_handler.emitEvent = emitEvent_test

    def tearDown(self):
        """
        Revert patching done to the event handler.
        """
        try:
            self.assertEventsQueueIsEmpty(tear_down=True)
            events_handler.emitEvent = self.emitEvent_good
            super(EventTestCase, self).tearDown()
        finally:
            self.clearEvents()

    def assertEvent(self, event_id, data=None, message=None, tear_down=False):
        '''Check that the system have issues and log with `log_id`.

        If `regex` is not None, the log text is checked agains the
        specified regular expression.
        '''
        if tear_down and not self._caller_success_member:
            return

        if data is None:
            data = {}

        try:
            first_entry = self._queue.popleft()
        except IndexError:
            self.fail(
                u'Events queue is empty. No sign of event with id=%s' % (
                event_id))

        if message:
            if message != first_entry.message:
                self.fail(
                    u'Event with d="%s" does not contains message "%s" '
                    u'but rather "%s"' % (
                        event_id, message, first_entry.message))

        if event_id != first_entry.id:
            self.fail(
                u'Top of the event queue does not contain the event with '
                u'id="%s" but rather "%s"' % (
                    event_id, unicode(first_entry)))

        self._checkData(
            kind=u'Event',
            kind_id=event_id,
            expected_data=data,
            current_data=first_entry.data,
            )

    def popEvent(self):
        """
        Extract and return the log from the queue.
        """
        return self._queue.popleft()

    def clearEvents(self):
        """
        Remove all current entries from the events queue.
        """
        self._queue.clear()

    def assertEventsQueueIsEmpty(self, tear_down=False):
        """
        Check that events queue is empty.
        """
        if tear_down and not self._caller_success_member:
            # When called from tearDown, only check for log if the
            # test was succesful. This prevent raising multiple failures
            # for a single error.
            return

        if len(self._queue) > 0:
            self.fail(u'Events queue is _not_ empty. %s' % repr(self._queue))

    def loadJSON(self, content):
        """
        Return the dictionary for encoded JSON.
        """
        return json.loads(content)

    def dumpJSON(self, content):
        """
        Return the serialized version of JSON content.
        """
        return json.dumps(content)


class LogTestCase(UtilsTestCase):
    '''A test factory which checks that all log messages were tested.'''

    def setUp(self):
        '''Redirect logging messages to local logging stack.'''
        super(LogTestCase, self).setUp()

        def log_test(message_id, text, avatar=None, peer=None, data=None):
            '''Push the logging message into the log testing queue.'''
            self.log_queue.append((message_id, text, avatar, peer, data))

        self.log_queue = deque([])
        self.log_method_good = Logger._log_helper
        self._patched_method = log_test
        Logger._log_helper = self._patched_method

    def tearDown(self):
        '''Revert monkey patching done to the Logger.'''
        try:
            self.assertLogIsEmpty(tear_down=True)
            Logger._log_helper = self.log_method_good
            super(LogTestCase, self).tearDown()
        finally:
            self.clearLog()

    def assertLog(self, log_id, regex=None, tear_down=False):
        '''Check that the system have issues and log with `log_id`.

        If `regex` is not None, the log text is checked against the
        specified regular expression.
        '''
        if tear_down and not self._caller_success_member:
            return

        first_log_entry = (0, '', '')
        try:
            first_log_entry = self.log_queue[0]
        except IndexError:
            self.fail(u'Log queue is empty. No sign of message with id=%d' % (
                log_id))

        queue_log_id = first_log_entry[0]
        queue_log_text = first_log_entry[1]
        if not log_id == queue_log_id:
            self.fail(
                u'Top of the queue does not contain the message with '
                u'id="%d" but rather "%s"' % (
                    log_id, unicode(first_log_entry)))
        elif regex and re.search(regex, queue_log_text) is None:
            self.fail(
                u'Top of the queue does not contain the message with '
                u'regex="%s" but rather text="%s"' % (
                    regex, unicode(first_log_entry)))
        else:
            # Everthing looks fine so we remove the log from the queue
            self.log_queue.popleft()

    def popLog(self):
        '''Return and extract the log from the queue.'''
        return self.log_queue.popleft()

    def clearLog(self):
        '''Remove all current entries from the log queue.'''
        self.log_queue.clear()

    def assertLogIsEmpty(self, tear_down=False):
        '''Check that the log queue is empty.'''
        if tear_down and not self._caller_success_member:
            # When called from tearDown, only check for log if the
            # test was succesful. This prevent raising multiple failures
            # for a single error.
            return

        if len(self.log_queue) > 0:
            self.fail(u'Log queue is _not_ empty. %s' % repr(self.log_queue))
