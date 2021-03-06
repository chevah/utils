# -*- coding: utf-8 -*-
# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.

# Make sure the values are in lowercase.
CONFIGURATION_DISABLED_VALUE = 'disabled'
CONFIGURATION_DISABLED_VALUES = ['none', 'disable', 'disabled']

CONFIGURATION_SECTION_LOG = u'log'

CONFIGURATION_INHERIT = [u'inherit', u'inherited']

# RSA and DSA keys.
DEFAULT_PUBLIC_KEY_EXTENSION = u'.pub'
DEFAULT_KEY_SIZE = 1024
DEFAULT_KEY_TYPE = u'rsa'

# File modes.
DEFAULT_FILE_MODE = 0666
DEFAULT_FOLDER_MODE = 0777

# Logger constants.
LOGGER_NAME = u'ChevahLogger'
LOGGER_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

CONFIGURATION_ALL_LOG_ENABLED_GROUPS = u'all'

# Log configuration section.
LOG_SECTION_DEFAULTS = {
    'log_enabled': True,
    'log_file': u'',
    'log_file_rotate_external': False,
    'log_file_rotate_at_size': 0,
    'log_file_rotate_each': '0 seconds',
    'log_file_rotate_count': 0,
    'log_syslog': u'',
    'log_windows_eventlog': u'',
    'log_enabled_groups': CONFIGURATION_ALL_LOG_ENABLED_GROUPS,
}


# Values for each account type
ACCOUNT_TYPE_OS = 1
ACCOUNT_TYPE_SFTPPLUS = 2
ACCOUNT_TYPE_APPLICATION = 3
ACCOUNT_TYPE_LOCAL_MANAGER = 4
ACCOUNT_TYPE_EXTERNAL = 5
ACCOUNT_TYPE_GROUP = 6
