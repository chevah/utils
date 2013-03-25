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

    It also contains the 'enabled' property for consistency, but right now
    it does nothting.

    [log]
    log_file: /path/to/file
    log_file_rotate_external: Yes | No
    log_file_rotate_at_size: 0 | Disabled
    log_file_rotate_each:
        1 hour | 2 seconds | 2 midnight | 3 Monday | Disabled
    log_file_rotate_count: 3 | 0 | Disabled
    log_syslog: /path/to/syslog/pype | syslog.host:port
    log_enabled_groups: all
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
                self._section_name, self._section_name + '_syslog')
        if syslog is None:
            return None

        # See if we can make an IP address out of the value.
        # For IP address we must return a (IP, PORT) tuple
        # For files we just return the value.
        search = re.search('(.*):(\d+)$', syslog)
        if search:
            return (search.groups()[0], int(search.groups()[1]))
        else:
            return syslog

    @property
    def file(self):
        '''Return the file path where logs are sent.'''
        return self._proxy.getStringOrNone(
                self._section_name, self._section_name + '_file')

    @property
    def file_rotate_external(self):
        '''Return log_file_rotate_external.'''
        return self._proxy.getBoolean(
                self._section_name,
                self._section_name + '_file_rotate_external')

    @property
    def file_rotate_count(self):
        '''Return log_file_rotate_count.'''
        value = self._proxy.getIntegerOrNone(
                self._section_name,
                self._section_name + '_file_rotate_count')
        if value is None:
            value = 0
        return value

    @property
    def file_rotate_at_size(self):
        '''Return log_file_rotate_at_size.'''
        value = self._proxy.getIntegerOrNone(
                self._section_name,
                self._section_name + '_file_rotate_at_size')
        if value is None:
            value = 0
        return value

    @property
    def file_rotate_each(self):
        '''Return log_file_rotate_at_size.

        Returns a tuple of (interval_count, inteval_type).

        1 hour | 2 seconds | 2 midnight | 3 Monday | Disabled
        '''
        value = self._proxy.getStringOrNone(
                self._section_name,
                self._section_name + '_file_rotate_each')
        if value is None:
            return value

        tokens = re.split('\W+', value)

        def get_rotate_each_error(details):
            return UtilsError(u'1023',
                _(u'Wrong value for logger rotation based on time interval. '
                  u'%s' % (details)))

        if len(tokens) != 2:
            raise get_rotate_each_error(_(u'Got: "%s"' % (value)))

        try:
            interval = int(tokens[0])
        except ValueError:
            raise get_rotate_each_error(
                _(u'Interval is not an integer. Got: "%s"' % (tokens[0])))

        when = tokens[1].lower()
        if when in ['second', 'seconds']:
            when = 's'
        elif when in ['minute', 'minutes']:
            when = 'm'
        elif when in ['hour', 'hours']:
            when = 'h'
        elif when in ['day', 'days']:
            when = 'd'
        elif when in ['midnight', 'midnights']:
            when = 'midnight'
        elif when in ['monday', 'mondays']:
            when = 'w0'
        elif when in ['tuesday', 'tuesdays']:
            when = 'w1'
        elif when in ['wednesday', 'wednesdays']:
            when = 'w2'
        elif when in ['thursday', 'thursdays']:
            when = 'w3'
        elif when in ['friday', 'friday']:
            when = 'w4'
        elif when in ['saturday', 'saturdays']:
            when = 'w5'
        elif when in ['sunday', 'sundays']:
            when = 'w6'
        else:
            raise get_rotate_each_error(
                _(u'Unknown interval type. Got: "%s"' % (tokens[1])))
        return (interval, when)

    def _sendNotify(self, option, initial_value, current_value):
        '''Generic notifier when a log section value changed.'''
        signal = Signal(
              self, initial_value=initial_value, current_value=current_value)
        self.notify(option, signal)

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
