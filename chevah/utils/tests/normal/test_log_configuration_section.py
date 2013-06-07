# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
from __future__ import with_statement

from chevah.utils.constants import LOG_SECTION_DEFAULTS
from chevah.utils.exceptions import UtilsError
from chevah.utils.interfaces import ILogConfigurationSection
from chevah.utils.testing import manufacture, UtilsTestCase


class TestLogConfigurationSection(UtilsTestCase):

    def _getSection(self, content=None):
        """
        Return a log configuration section.
        """
        if content is None:
            content = (
                '[log]\n'
                'log_file: Disable\n'
                )
        proxy = manufacture.makeFileConfigurationProxy(
            content=content, defaults=LOG_SECTION_DEFAULTS)
        return manufacture.makeLogConfigurationSection(proxy=proxy)

    def test_init_empty(self):
        """
        Check default values for log configuration section.
        """
        content = (
            '[log]\n'
            )
        section = self._getSection(content)

        self.assertProvides(ILogConfigurationSection, section)
        self.assertEqual(u'log', section._section_name)
        self.assertEqual(u'log', section._prefix)

        self.assertIsNone(section.file)
        self.assertFalse(section.file_rotate_external)
        self.assertEqual(0, section.file_rotate_at_size)
        self.assertIsNone(section.file_rotate_each)
        self.assertEqual(0, section.file_rotate_count)
        self.assertIsNone(section.syslog)
        self.assertIsNone(section.windows_eventlog)
        self.assertEqual([u'all'], section.enabled_groups)

    def test_file_disabled_as_none(self):
        """
        Check reading log_file when is disabled.
        """
        content = (
            '[log]\n'
            'log_file: None\n'
            )

        section = self._getSection(content)

        self.assertIsNone(section.file)

    def test_file_disabled(self):
        """
        Check reading log_file when is disabled.
        """
        content = (
            '[log]\n'
            'log_file: Disable\n'
            )

        section = self._getSection(content)

        self.assertIsNone(section.file)

    def test_file_update(self):
        """
        log_file can be updated at runtime and it will notify the change.
        """
        new_value = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_file: Disable\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('file', callback)

        section.file = new_value

        self.assertEqual(new_value, section.file)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(new_value, signal.current_value)

    def test_file_rotate_external_true(self):
        """
        Check reading log_file_rotate_external.
        """
        content = (
            '[log]\n'
            'log_file_rotate_external: Yes\n'
            )

        section = self._getSection(content)

        self.assertTrue(section.file_rotate_external)

    def test_file_rotate_external_false(self):
        """
        Check reading log_file_rotate_external.
        """
        content = (
            '[log]\n'
            'log_file_rotate_external: No\n'
            )

        section = self._getSection(content)

        self.assertFalse(section.file_rotate_external)

    def test_file_rotate_external_update(self):
        """
        It can be updated at runtime.
        """
        content = (
            '[log]\n'
            'log_file_rotate_external: No\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('file_rotate_external', callback)

        section.file_rotate_external = True

        self.assertTrue(section.file_rotate_external)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(True, signal.current_value)

    def test_file_rotate_count_disabled(self):
        """
        Check reading log_file_rotate_external.
        """
        content = (
            '[log]\n'
            'log_file_rotate_count: Disabled\n'
            )

        section = self._getSection(content)

        self.assertEqual(0, section.file_rotate_count)

    def test_file_rotate_count_some_value(self):
        """
        Check reading log_file_rotate_count.
        """
        content = (
            '[log]\n'
            'log_file_rotate_count: 7\n'
            )

        section = self._getSection(content)

        self.assertEqual(7, section.file_rotate_count)

    def test_file_rotate_count_update(self):
        """
        log_file_rotate_count can be updated at runtime.
        """
        new_value = manufacture.getUniqueInteger()
        content = (
            '[log]\n'
            'log_file_rotate_count: 7\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('file_rotate_count', callback)

        section.file_rotate_count = new_value

        self.assertEqual(new_value, section.file_rotate_count)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(new_value, signal.current_value)

    def test_file_rotate_at_size_disabled(self):
        """
        Check reading log_file_rotate_at_size.
        """
        content = (
            '[log]\n'
            'log_file_rotate_at_size: Disabled\n'
            )

        section = self._getSection(content)

        self.assertEqual(0, section.file_rotate_at_size)

    def test_file_rotate_at_size_some_value(self):
        """
        Check reading log_file_rotate_at_size.
        """
        content = (
            '[log]\n'
            'log_file_rotate_at_size: 7\n'
            )

        section = self._getSection(content)

        self.assertEqual(7, section.file_rotate_at_size)

    def test_file_rotate_at_size_update(self):
        """
        log_file_rotate_at_size can be updated at runtime
        """
        new_value = manufacture.getUniqueInteger()
        content = (
            '[log]\n'
            'log_file_rotate_at_size: 7\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('file_rotate_at_size', callback)

        section.file_rotate_at_size = new_value

        self.assertEqual(new_value, section.file_rotate_at_size)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(new_value, signal.current_value)

    def test_file_rotate_each_disabled(self):
        """
        Check reading log_file_rotate_each.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: Disabled\n'
            )

        section = self._getSection(content)

        self.assertIsNone(section.file_rotate_each)

    def test_file_rotate_each_bad_interval(self):
        """
        Check reading log_file_rotate_each.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: one hours\n'
            )

        section = self._getSection(content)

        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each

        self.assertEqual(u'1023', context.exception.event_id)

    def test_file_rotate_each_bad_interval_type(self):
        """
        An error is raised when a bad interval type is provided for
        log_file_rotate_each.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 4 Moons\n'
            )

        section = self._getSection(content)

        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each

        self.assertEqual(u'1023', context.exception.event_id)

    def test_file_rotate_each_negative_internal(self):
        """
        An error is raised when a interval is a negative value.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: -4 days\n'
            )

        section = self._getSection(content)

        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each

        self.assertEqual(u'1023', context.exception.event_id)

    def test_file_rotate_each_second(self):
        """
        Check reading log_file_rotate_each for second.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 4 Seconds\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(4, interval)
        self.assertEqual(u's', when)

    def test_file_rotate_each_minute(self):
        """
        Check reading log_file_rotate_each for minute.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 0 minute\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(0, interval)
        self.assertEqual(u'm', when)

    def test_file_rotate_each_hour(self):
        """
        Check reading log_file_rotate_each for hour.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 1 hour\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(1, interval)
        self.assertEqual(u'h', when)

    def test_file_rotate_each_day(self):
        """
        Check reading log_file_rotate_each for day.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 5 day\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(5, interval)
        self.assertEqual(u'd', when)

    def test_file_rotate_each_midnight(self):
        """
        Check reading log_file_rotate_each for midnight.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 2 midnight\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(2, interval)
        self.assertEqual(u'midnight', when)

    def test_file_rotate_each_monday(self):
        """
        Check reading log_file_rotate_each for Monday.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 2 Monday\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(2, interval)
        self.assertEqual(u'w0', when)

    def test_file_rotate_each_tuesday(self):
        """
        Check reading log_file_rotate_each for tuesday.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 2 tuesday\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(2, interval)
        self.assertEqual(u'w1', when)

    def test_file_rotate_each_wednesday(self):
        """
        Check reading log_file_rotate_each for wednesdays.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 2 wednesdays\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(2, interval)
        self.assertEqual(u'w2', when)

    def test_file_rotate_each_thursday(self):
        """
        Check reading log_file_rotate_each for thursdays.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 4 thursdays\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(4, interval)
        self.assertEqual(u'w3', when)

    def test_file_rotate_each_friday(self):
        """
        Check reading log_file_rotate_each for friday.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 4 friday\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(4, interval)
        self.assertEqual(u'w4', when)

    def test_file_rotate_each_saturday(self):
        """
        Check reading log_file_rotate_each for saturday.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 4 saturday\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(4, interval)
        self.assertEqual(u'w5', when)

    def test_file_rotate_each_sunday(self):
        """
        Check reading log_file_rotate_each for sunday.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 4 sunday\n'
            )

        section = self._getSection(content)

        (interval, when) = section.file_rotate_each
        self.assertEqual(4, interval)
        self.assertEqual(u'w6', when)

    def test_file_rotate_each_update(self):
        """
        file_rotate_each can be updated at runtime as tuple or list and the
        parsed value is returned.

        When set to empty string, Disabled or None, will return `None`.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: Disabled\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('file_rotate_each', callback)

        section.file_rotate_each = (5, 'w0')

        (interval, when) = section.file_rotate_each
        self.assertEqual(5, interval)
        self.assertEqual(u'w0', when)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual((5, 'w0'), signal.current_value)

        section.file_rotate_each = [6, 'w1']

        (interval, when) = section.file_rotate_each
        self.assertEqual(6, interval)
        self.assertEqual(u'w1', when)

    def test_file_rotate_each_update_disabled(self):
        """
        It can be updated to disabled values and it will return `None`.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: 1 day\n'
            )
        section = self._getSection(content)

        section.file_rotate_each = 'Disabled'
        self.assertIsNone(section.file_rotate_each)

        section.file_rotate_each = ''
        self.assertIsNone(section.file_rotate_each)

        section.file_rotate_each = None
        self.assertIsNone(section.file_rotate_each)

    def test_file_rotate_each_failure(self):
        """
        An error is raised when trying to set an invalid option.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: Disabled\n'
            )
        section = self._getSection(content)

        # Check unknown interval type.
        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each = (5, 'unknown')

        self.assertExceptionID(u'1023', context.exception)

        # Check non-string value.
        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each = ('bla', 'w0')

        self.assertExceptionID(u'1023', context.exception)

        # Check negative value.
        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each = (-1, 'w0')

        self.assertExceptionID(u'1023', context.exception)

    def test_syslog_disabled(self):
        """
        Check reading log_syslog as disabled value.
        """
        content = (
            '[log]\n'
            'log_syslog: Disable\n'
            )

        section = self._getSection(content)

        self.assertIsNone(section.syslog)

    def test_syslog_hostname(self):
        """
        When syslog is configured as hosname:IP a tuple is returned.
        """
        content = (
            '[log]\n'
            'log_syslog: localhost:514\n'
            )

        section = self._getSection(content)

        self.assertTupleEqual(('localhost', 514), section.syslog)

    def test_syslog_path(self):
        """
        Check reading log_syslog as a path.
        """
        content = (
            '[log]\n'
            'log_syslog: /dev/log\n'
            )

        section = self._getSection(content)

        self.assertEqual(u'/dev/log', section.syslog)

    def test_syslog_change(self):
        """
        It can be changed at runtime
        """
        new_path = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_syslog: /dev/log\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('syslog', callback)

        section.syslog = new_path

        self.assertEqual(new_path, section.syslog)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(new_path, signal.current_value)

    def test_enabled_groups_empty(self):
        """
        When no group is defined, enabled_groups is empty.
        """
        content = (
            '[log]\n'
            'log_enabled_groups:\n'
            )

        section = self._getSection(content)

        self.assertEqual([], section.enabled_groups)

    def test_enabled_groups_update(self):
        """
        Enabled_groups will return a list and will be updated using a list.

        Values are case insensitive.
        """
        content = (
            '[log]\n'
            'log_enabled_groups: some, Value,\n'
            )

        section = self._getSection(content)

        self.assertEqual([u'some', u'value'], section.enabled_groups)

        # Updating to empty group.
        section.enabled_groups = []
        self.assertEqual([], section.enabled_groups)

        # Updating to new list.
        section.enabled_groups = [u'new', u'LiSt']
        self.assertEqual([u'new', u'list'], section.enabled_groups)

    def test_windows_eventlog_disabled(self):
        """
        None is returned when windows_eventlog is disabled.
        """
        content = (
            '[log]\n'
            'log_windows_eventlog: Disabled\n'
            )

        section = self._getSection(content)

        self.assertIsNone(section.windows_eventlog)

    def test_windows_eventlog_value(self):
        """
        The source name is returned for defiend windows_eventlog.
        """
        content = (
            '[log]\n'
            'log_windows_eventlog: something\n'
            )

        section = self._getSection(content)

        self.assertEqual(u'something', section.windows_eventlog)

    def test_windows_eventlog_change(self):
        """
        It can be updated at runtime.
        """
        new_value = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_windows_eventlog: something\n'
            )
        callback = self.Mock()
        section = self._getSection(content)
        section.subscribe('windows_eventlog', callback)

        section.windows_eventlog = new_value

        self.assertEqual(new_value, section.windows_eventlog)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(new_value, signal.current_value)

    def test_updateWithNotify_valid(self):
        """
        When notifications don't raise any error, the value is kept.
        """
        section = self._getSection()
        initial_value = manufacture.string()
        section.file = initial_value
        value = manufacture.string()
        self._callback_called = False

        def callback(signal):
            self._callback_called = True
            # Check that during the notification, the new value
            # is already set.
            self.assertEqual(value, section.file)
            # Check signal values.
            self.assertEqual(section, signal.source)
            self.assertEqual(initial_value, signal.initial_value)
            self.assertEqual(value, signal.current_value)

        section.subscribe('file', callback)

        section._updateWithNotify(
            setter=section._proxy.setStringOrNone, name='file', value=value)

        self.assertEqual(value, section.file)
        self.assertTrue(self._callback_called)

    def test_updateWithNotify_failed_notification(self):
        """
        When notifications fails, the value is restored and error re-raised.
        """
        section = self._getSection()
        initial_value = manufacture.string()
        section.file = initial_value
        value = manufacture.string()
        callback = self.Mock(side_effect=[AssertionError('fail')])
        section.subscribe('file', callback)

        with self.assertRaises(AssertionError) as context:
            section._updateWithNotify(
                setter=section._proxy.setStringOrNone,
                name='file',
                value=value,
                )

        self.assertEqual(initial_value, section.file)
        self.assertEqual('fail', context.exception.message)
