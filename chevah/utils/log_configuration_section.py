# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Configuration section for Chevah logger.'''
from chevah.utils import __python_future__

import re

from zope.interface import implements

from chevah.utils.configuration import ConfigurationSectionMixin
from chevah.utils.constants import (
    CONFIGURATION_SECTION_LOG,
    )
from chevah.utils.exceptions import UtilsError
from chevah.utils.interfaces import ILogConfigurationSection
from chevah.utils.helpers import _
from chevah.utils.observer import Signal


class LogConfigurationSection(ConfigurationSectionMixin):
    '''Configurations for the log section.

    [log]
    log_file: /path/to/file
    log_file_rotate_external: Yes | No
    log_file_rotate_at_size: 0 | Disabled
    log_file_rotate_each:
        1 hour | 2 seconds | 2 midnight | 3 Monday | Disabled
    log_file_rotate_count: 3 | 0 | Disabled
    log_syslog: /path/to/syslog/pipe | syslog.host:port
    log_enabled_groups: all
    log_windows_eventlog: sftpplus-server
    '''

    implements(ILogConfigurationSection)

    def __init__(self, proxy):
        self._proxy = proxy
        self._section_name = CONFIGURATION_SECTION_LOG
        self._prefix = u'log'

    @property
    def syslog(self):
        '''Return the syslog address used for logging.

        server_log_syslog can be a path to a file or a host:port address.
        '''
        syslog = self._proxy.getStringOrNone(
                self._section_name, self._prefix + '_syslog')
        if not syslog:
            return None

        # See if we can make an IP address out of the value.
        # For IP address we must return a (IP, PORT) tuple
        # For files we just return the value.
        search = re.search('(.*):(\d+)$', syslog)
        if search:
            return (search.groups()[0], int(search.groups()[1]))
        else:
            return syslog

    @syslog.setter
    def syslog(self, value):
        self._updateWithNotify(
            setter=self._proxy.setStringOrNone, name='syslog', value=value)

    def _updateWithNotify(self, setter, name, value):
        """
        Update configuration and notify changes.

        Revert configuration on error.
        """
        initial_value = getattr(self, name)
        configuration_option_name = self._prefix + '_' + name
        setter(self._section_name, configuration_option_name, value)
        current_value = getattr(self, name)

        signal = Signal(
              self, initial_value=initial_value, current_value=current_value)
        try:
            self.notify(name, signal)
        except:
            setter(
                self._section_name, configuration_option_name, initial_value)
            raise

    @property
    def file(self):
        '''Return the file path where logs are sent.'''
        return self._proxy.getStringOrNone(
                self._section_name, self._section_name + '_file')

    @file.setter
    def file(self, value):
        self._updateWithNotify(
            setter=self._proxy.setStringOrNone, name='file', value=value)

    @property
    def file_rotate_external(self):
        '''Return log_file_rotate_external.'''
        return self._proxy.getBoolean(
                self._section_name,
                self._prefix + '_file_rotate_external')

    @file_rotate_external.setter
    def file_rotate_external(self, value):
        self._updateWithNotify(
            setter=self._proxy.setBoolean,
            name='file_rotate_external',
            value=value,
            )

    @property
    def file_rotate_count(self):
        '''Return log_file_rotate_count.'''
        value = self._proxy.getIntegerOrNone(
                self._section_name,
                self._prefix + '_file_rotate_count')
        if value is None:
            value = 0
        return value

    @file_rotate_count.setter
    def file_rotate_count(self, value):
        self._updateWithNotify(
            setter=self._proxy.setIntegerOrNone,
            name='file_rotate_count',
            value=value,
            )

    @property
    def file_rotate_at_size(self):
        '''Return log_file_rotate_at_size.'''
        value = self._proxy.getIntegerOrNone(
                self._section_name,
                self._prefix + '_file_rotate_at_size')
        if value is None:
            value = 0
        return value

    @file_rotate_at_size.setter
    def file_rotate_at_size(self, value):
        self._updateWithNotify(
            setter=self._proxy.setIntegerOrNone,
            name='file_rotate_at_size',
            value=value,
            )

    @property
    def file_rotate_each(self):
        """
        Return log_file_rotate_at_each.

        Returns a tuple of (interval_count, inteval_type).
        """
        value = self._proxy.getStringOrNone(
                self._section_name,
                self._prefix + '_file_rotate_each')
        return self._fileRotateEachToMachineReadable(value)

    @file_rotate_each.setter
    def file_rotate_each(self, value):
        if not value:
            update_value = None
        elif (isinstance(value, basestring) and
                self._proxy.isDisabledValue(value)
            ):
            update_value = None
        else:
            update_value = self._fileRotateEachToHumanReadable(value)

        self._updateWithNotify(
            setter=self._proxy.setStringOrNone,
            name='file_rotate_each',
            value=update_value,
            )

    def _fileRotateEachToMachineReadable(self, value):
        """
        Return the machine readable format for `value`.

        Inside the configuration file, the value is stored as a human
        readable format like::

            1 hour | 2 seconds | 2 midnight | 3 Monday | Disabled

        When reading the value, it will return::

            (1, 'h') | (2, 's') | (2, 'midnight') | (3, 'w0') | None
        """

        mapping = {
            u'second': u's',
            u'seconds': u's',
            u'minute': u'm',
            u'minutes': u'm',
            u'hour': u'h',
            u'hours': u'h',
            u'day': u'd',
            u'days': u'd',
            u'midnight': u'midnight',
            u'midnights': u'midnight',
            u'monday': u'w0',
            u'mondays': u'w0',
            u'tuesday': u'w1',
            u'tuesdays': u'w1',
            u'wednesday': u'w2',
            u'wednesdays': u'w2',
            u'thursday': u'w3',
            u'thursdays': u'w3',
            u'friday': u'w4',
            u'fridays': u'w4',
            u'saturday': u'w5',
            u'saturdays': u'w5',
            u'sunday': u'w6',
            u'sundays': u'w6',
            }

        if not value:
            return None

        tokens = re.split('\W+', value)

        if len(tokens) != 2:
            raise self._fileRotateEachError(_(u'Got: "%s"' % (value)))

        try:
            interval = int(tokens[0])
        except ValueError:
            raise self._fileRotateEachError(
                _(u'Interval is not an integer. Got: "%s"' % (tokens[0])))

        if interval < 0:
            raise self._fileRotateEachError(
                _(u'Interval should not be less than 0'))

        when = tokens[1].lower()
        try:
            when = mapping[when]
        except KeyError:
            raise self._fileRotateEachError(
                _(u'Unknown interval type. Got: "%s"' % (tokens[1])))
        return (interval, when)

    def _fileRotateEachToHumanReadable(self, value):
        """
        Return the human readable representation for file_rotate_each
        tuple provided as `value'.

        (2, 's') returns 2 seconds
        """
        mapping = {
            u's': u'second',
            u'm': u'minute',
            u'h': u'hour',
            u'd': u'day',
            u'midnight': u'midnight',
            u'w0': u'monday',
            u'w1': u'tuesday',
            u'w2': u'wednesday',
            u'w3': u'thursday',
            u'w4': u'friday',
            u'w5': u'saturday',
            u'w6': u'sunday',
            }
        try:
            frequency = int(value[0])
        except ValueError:
            raise self._fileRotateEachError(
                _(u'Bad interval count. Got: "%s"' % (value[0])))

        if frequency < 0:
            raise self._fileRotateEachError(
                _(u'Interval should not be less than 0'))

        try:
            when = mapping[value[1]]
        except KeyError:
            raise self._fileRotateEachError(
                _(u'Unknown interval type. Got: "%s"' % (value[1])))

        return u'%s %s' % (frequency, when)

    def _fileRotateEachError(self, details):
        return UtilsError(u'1023',
            _(u'Wrong value for logger rotation based on time interval. '
              u'%s' % (details)))

    @property
    def enabled_groups(self):
        '''Return the list of enabled log groups.'''
        value = self._proxy.getString(
                self._section_name, self._prefix + '_enabled_groups')
        groups = []
        for group in value.split(','):
            group = group.strip()
            if group:
                groups.append(group.lower())

        return groups

    @enabled_groups.setter
    def enabled_groups(self, value):
        '''Set the list of enabled groups.'''
        self._proxy.setString(
            self._section_name,
            self._prefix + '_enabled_groups',
            ', '.join(value),
            )

    @property
    def windows_eventlog(self):
        """
        Name of source used to log into Windows Event log.

        Returns None if event log is not enabled.
        """
        return self._proxy.getStringOrNone(
                self._section_name, self._prefix + '_windows_eventlog')

    @windows_eventlog.setter
    def windows_eventlog(self, value):
        self._updateWithNotify(
            setter=self._proxy.setStringOrNone,
            name='windows_eventlog',
            value=value,
            )
