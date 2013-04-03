# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
from __future__ import with_statement


from chevah.utils.exceptions import UtilsError
from chevah.utils.interfaces import ILogConfigurationSection
from chevah.utils.testing import manufacture, UtilsTestCase


class TestLogConfigurationSection(UtilsTestCase):

    def _getSection(self, content):
        proxy = manufacture.makeFileConfigurationProxy(content=content)
        return manufacture.makeLogConfigurationSection(proxy=proxy)

    def test_init(self):
        """
        LogConfigurationSection
        """
        content = (
            '[log]\n'
            'log_file: None\n'
            'log_file_rotate_external: Yes\n'
            'log_file_rotate_at_size: 0\n'
            'log_file_rotate_each: 2 seconds\n'
            'log_file_rotate_count: Disabled\n'
            'log_enabled_groups: all\n'
            'log_syslog: Disabled\n'
            'log_windows_eventlog: Disabled\n'
            )
        section = self._getSection(content)

        self.assertProvides(ILogConfigurationSection, section)
        self.assertEqual(u'log', section._section_name)
        self.assertEqual(u'log', section._prefix)

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
        log_file can be updated at runtime.
        """
        new_value = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_file: Disable\n'
            )
        section = self._getSection(content)

        section.file = new_value

        self.assertEqual(new_value, section.file)


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
        og_file_rotate_external can be updated at runtime.
        """
        content = (
            '[log]\n'
            'log_file_rotate_external: No\n'
            )

        section = self._getSection(content)

        section.file_rotate_external = True

        self.assertTrue(section.file_rotate_external)

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
        section = self._getSection(content)

        section.file_rotate_count = new_value

        self.assertEqual(new_value, section.file_rotate_count)

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
        section = self._getSection(content)

        section.file_rotate_at_size = new_value

        self.assertEqual(new_value, section.file_rotate_at_size)

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

    def test_file_rotate_each_bad_format(self):
        """
        Check reading log_file_rotate_each.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: every 2 hours\n'
            )

        section = self._getSection(content)

        with self.assertRaises(UtilsError) as context:
            section.file_rotate_each

        self.assertEqual(u'1023', context.exception.event_id)

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
        self.assertEqual('s', when)

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
        self.assertEqual('m', when)

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
        self.assertEqual('h', when)

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
        self.assertEqual('d', when)

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
        self.assertEqual('midnight', when)

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
        self.assertEqual('w0', when)

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
        self.assertEqual('w1', when)

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
        self.assertEqual('w2', when)

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
        self.assertEqual('w3', when)

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
        self.assertEqual('w4', when)

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
        self.assertEqual('w5', when)

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
        self.assertEqual('w6', when)

    def test_file_rotate_each_update(self):
        """
        file_rotate_each can be updated at runtime as string and the
        parsed value is returned.

        When set to Disabled or None, will return none.
        """
        content = (
            '[log]\n'
            'log_file_rotate_each: Disabled\n'
            )
        section = self._getSection(content)

        section.file_rotate_each = '5 monday'

        (interval, when) = section.file_rotate_each
        self.assertEqual(5, interval)
        self.assertEqual('w0', when)

        section.file_rotate_each = 'Disabled'
        self.assertIsNone(section.file_rotate_each)

        section.file_rotate_each = None
        self.assertIsNone(section.file_rotate_each)

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
        log_syslog can be changed at runtime
        """
        new_path = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_syslog: /dev/log\n'
            )
        section = self._getSection(content)

        section.syslog = new_path

        self.assertEqual(new_path, section.syslog)

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
        windows_eventlog can be changed at runtime.
        """
        new_value = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_windows_eventlog: something\n'
            )
        section = self._getSection(content)

        section.windows_eventlog = new_value

        self.assertEqual(new_value, section.windows_eventlog)
