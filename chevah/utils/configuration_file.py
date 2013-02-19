# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Module for configuration loaded from local files.'''
from chevah.utils import __python_future__

import ConfigParser

from zope.interface import implements

from chevah.compat import local_filesystem
from chevah.utils.constants import (
    CONFIGURATION_DISABLED_VALUE,
    CONFIGURATION_DISABLED_VALUES,
    CONFIGURATION_INHERIT,
    )
from chevah.utils.exceptions import (
    UtilsError,
    NoSuchPropertyError,
    NoSuchSectionError,
    ReadOnlyPropertyError,
    )
from chevah.utils.helpers import _
from chevah.utils.interfaces import (
    IConfiguration,
    IConfigurationProxy,
    IConfigurationSection,
    PublicAttribute,
    PublicWritableAttribute
    )
from chevah.utils.observer import Signal, ObserverMixin


class ChevahConfigParser(object, ConfigParser.ConfigParser):
    '''Chevah .ini format parser.'''

    def __init__(self, defaults):
        super(ChevahConfigParser, self).__init__(defaults)


class FileConfigurationProxy(object):
    '''Config parser for Chevah projects.'''

    implements(IConfigurationProxy)

    def __init__(self, configuration_path=None, configuration_file=None,
                 defaults=None):
        self._raw_config = ConfigParser.SafeConfigParser(defaults)
        self._configuration_path = configuration_path
        if configuration_path:
            configuration_segments = local_filesystem.getSegmentsFromRealPath(
                configuration_path)
            if not local_filesystem.isFile(configuration_segments):
                raise UtilsError(u'1011', _(
                    u'Configuration file "%s" does not exists.' % (
                        configuration_path)))
            try:
                self._configuration_file = (
                    local_filesystem.openFileForReading(
                         configuration_segments, utf8=True))
            except IOError:
                raise UtilsError(u'1012', _(
                    u'Server process could not read the configuration file '
                    u'"%s".' % (configuration_path))
                    )
        elif configuration_file:
            self._configuration_file = configuration_file
        else:
            raise AssertionError('You must specify a path or a file.')

    def load(self):
        '''Load configuration from input file.'''
        try:
            self._raw_config.readfp(self._configuration_file)
        except (ConfigParser.ParsingError, AttributeError), error:
            self._configuration_file = None
            message = error.message
            if not isinstance(message, unicode):
                message = message.decode('utf-8')
            raise UtilsError(u'1002', _(
                u'Could not parse the configuration file. %s' % (message))
                )
        else:
            self._configuration_file.close()

    def save(self):
        '''Store the configuration into file.'''
        if self._configuration_path:
            real_segments = local_filesystem.getSegmentsFromRealPath(
                self._configuration_path)
            tmp_segments = real_segments[:]
            tmp_segments[-1] = tmp_segments[-1] + u'.tmp'
            store_file = local_filesystem.openFileForWriting(
                    tmp_segments, utf8=True)
            for section in self._raw_config._sections:
                store_file.write(u'[%s]\n' % section)
                items = self._raw_config._sections[section].items()
                for (key, value) in items:
                    if key != u'__name__':
                        store_file.write(u'%s = %s\n' %
                                 (key,
                                 unicode(value).replace(u'\n', u'\n\t')))
                store_file.write('\n')
            store_file.close()
            # We delete the file first to work arround windows problems.
            local_filesystem.deleteFile(real_segments)
            local_filesystem.rename(tmp_segments, real_segments)
        else:
            raise AssertionError(
                'Trying to save a configration that was not loaded from '
                ' a file')

    def get(self, section, option):
        '''Raise AssertionError if low level methods are called.'''
        assert False, 'Use getString instead of get.'

    def getboolean(self, section, option):
        '''Raise AssertionError if low level methods are called.'''
        assert False, 'Use getBoolean instead of getboolean.'

    def getfloat(self, section, option):
        '''Raise AssertionError if low level methods are called.'''
        assert False, 'Use getfloat instead of getFloat.'

    def hasSection(self, section):
        '''See `IConfigurationProxy`.'''
        return self._raw_config.has_section(section)

    def addSection(self, section):
        '''See `IConfigurationProxy`.'''
        self._raw_config.add_section(section)

    def removeSection(self, section):
        '''See `IConfigurationProxy`.'''
        return self._raw_config.remove_section(section)

    def hasOption(self, section, option):
        '''See `IConfigurationProxy'.'''
        return self._raw_config.has_option(section, option)

    @property
    def sections(self):
        '''See `IConfigurationProxy`.'''
        return self._raw_config.sections()

    def _call(self, method, section, option, type_string='', raw=False):
        try:
            if raw:
                return method(section, option, raw=True)
            else:
                return method(section, option)
        except ValueError, error:
            raise UtilsError(u'1000', _(
                u'Wrong %(type)s value for option "%(option)s" in '
                u'section "%(section)s". %(error_details)s' % {
                    'type': type_string,
                    'option': option,
                    'section': section,
                    'error_details': unicode(error),
                    }))
        except ConfigParser.NoOptionError, error:
            # If we ended up here it means that we have not defined a default
            # value for this option.
            error_message = (
                u'Configuration file does not have any option "%(option)s" '
                u'in section "%(section)s". You must add a default value.' % {
                    'option': option,
                    'section': section,
                    })
            raise AssertionError(error_message.encode('utf-8'))
        except ConfigParser.NoSectionError, error:
            # If we ended up here it means that we have not created the
            # default sections if they were missing.
            error_message = (
                u'Configuration file does not define section "%(section)s" '
                u'for storing the option "%(option)s". You must create this '
                u'section.' % {
                    'option': option,
                    'section': section,
                    })
            raise AssertionError(error_message.encode('utf-8'))
        raise AssertionError(
            u'All exceptions should have been previously catched for '
            'section:%s option:%s.' % (section, option))

    def getString(self, section, option):
        '''See `IConfigurationProxy`.'''
        value = self._call(
            self._raw_config.get, section, option, 'string', raw=True)
        if type(value) is not unicode:
            value = value.decode('utf-8')
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        return value

    def getStringOrNone(self, section, option):
        '''See `IConfigurationProxy`.'''
        value = self.getString(section, option)
        if value.lower() in CONFIGURATION_DISABLED_VALUES:
            return None
        else:
            return value

    def getStringOrInherit(self, section, option):
        value = self.getString(section, option)
        if value.lower() in CONFIGURATION_INHERIT:
            return CONFIGURATION_INHERIT[0]
        else:
            return value

    def getStringSpecial(self, section, option):
        value = self.getString(section, option)
        if value.lower() in CONFIGURATION_DISABLED_VALUES:
            return None

        if value.lower() in CONFIGURATION_INHERIT:
            return CONFIGURATION_INHERIT[0]

        return value

    def setString(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        return self._raw_config.set(section, option, value)

    def setStringOrNone(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        if value is None:
            value = CONFIGURATION_DISABLED_VALUE
        return self._raw_config.set(section, option, value)

    def setStringOrInherit(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        if value.lower() is CONFIGURATION_INHERIT:
            value = CONFIGURATION_INHERIT[0]
        self.setString(section, option, value)

    def setStringSpecial(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        if value is None:
            value = CONFIGURATION_DISABLED_VALUE
        elif value.lower() is CONFIGURATION_INHERIT:
            value = CONFIGURATION_INHERIT[0]
        self.setString(section, option, value)

    def getInteger(self, section, option):
        '''See `IConfigurationProxy`.'''
        return self._call(
            self._raw_config.getint, section, option, 'integer number')

    def getIntegerOrNone(self, section, option):
        '''See `IConfigurationProxy`.'''
        value = self.getString(section, option)
        if value.lower() in CONFIGURATION_DISABLED_VALUES:
            return None
        else:
            return self.getInteger(section, option)

    def setInteger(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        return self._raw_config.set(section, option, unicode(value))

    def setIntegerOrNone(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        if value is None:
            value = CONFIGURATION_DISABLED_VALUE
        return self._raw_config.set(section, option, unicode(value))

    def getBoolean(self, section, option):
        '''See `IConfigurationProxy`.'''
        return self._call(
            self._raw_config.getboolean, section, option, 'boolean')

    def getBooleanOrInherit(self, section, option):
        value = self.getString(section, option)
        if value.lower() in CONFIGURATION_INHERIT:
            return CONFIGURATION_INHERIT[0]

        return self.getBoolean(section, option)

    def setBoolean(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        return self._raw_config.set(section, option, unicode(value))

    def setBooleanOrInherit(self, section, option, value):
        '''See `IConfigurationProxy`.'''
        if value is True or value is False:
            self.setBoolean(section, option, value)
        elif value.lower() in CONFIGURATION_INHERIT:
            self.setString(
                section, option, CONFIGURATION_INHERIT[0])
        else:
            raise AssertionError('Not a boolean for Inherit value.')

    def getFloat(self, section, option):
        '''See `IConfigurationProxy`.'''
        return self._call(
            self._raw_config.getfloat, section, option, 'floating number')


class ConfigurationFileMixin(object):
    '''
    Basic code for all configuration files.

    Classes using this mixin should initialize the following members:
     * proxy - FileProxyConfiguration
     * section_names - list of section names
    '''

    implements(IConfiguration)

    def save(self):
        '''Store the configuration into file.'''
        self._proxy.save()

    def checkConfigurationFileAndPathArguments(
            self, configuration_path, configuration_file):
        '''Make sure that only path or file is specified.'''
        assert (
            (configuration_path and not configuration_file) or
            (not configuration_path and configuration_file)), (
                'Configuration objects must be initialized with either '
                'a configuration path or a configuration file stream!.')

    def addSection(self, section):
        self._proxy.addSection(section)

    def createMissingSections(self, valid_sections=None):
        '''Create any missing sections so that the default values will be
        enabled.'''
        assert self._proxy, (
            'You must load a configuration before creating missing sections.')
        if valid_sections is None:
            valid_sections = self.section_names
        for section in valid_sections:
            if not self._proxy.hasSection(section):
                self._proxy.addSection(section)

    def getAllProperties(self):
        """
        See `IConfiguration`.
        """
        result = {}
        for section in self.section_names:
            section_configuration = getattr(self, section, None)
            if section_configuration is None:
                from chevah.utils.logger import debug
                debug('Could not found section "%s".' % (section))
                continue
            section_properties = section_configuration.getAllProperties()
            result.update({section: section_properties})
        return result

    def setProperty(self, property_path, value):
        """
        See `IConfiguration`.
        """
        try:
            head, tail = property_path.split('/', 1)
        except ValueError:
            raise NoSuchPropertyError(property_path)

        if not head in self.section_names:
            raise NoSuchSectionError(head)

        section_configuration = getattr(self, head, None)
        if section_configuration is None:
            raise NoSuchPropertyError(property_path)

        section_configuration.setProperty(tail, value)


class ConfigurationSectionMixin(ObserverMixin):
    """
    Mixin for a configuration section.
    """

    implements(IConfigurationSection)

    def getAllProperties(self):
        """
        See `IConfigurationSection`.
        """
        result = {}

        for interface in self.__provides__.flattened():
            for name, description in interface.namesAndDescriptions():
                if not isinstance(description, PublicAttribute):
                    continue
                try:
                    value = getattr(self, name)
                except AttributeError:
                    raise NoSuchPropertyError(name)
                result.update({name: value})
        return result

    def setProperty(self, property_path, value):
        """
        See `IConfigurationSection`.
        """
        try:
            head, tail = property_path.split('/', 1)
        except ValueError:
            head = property_path
            tail = None

        if tail is not None:
            raise NoSuchPropertyError(property_path)

        for interface in self.__provides__.flattened():
            for name, description in interface.namesAndDescriptions():
                if name != head:
                    continue

                if not isinstance(description, PublicWritableAttribute):
                    raise ReadOnlyPropertyError(property_path)

                if not hasattr(self, name):
                    raise NoSuchPropertyError(property_path)

                setattr(self, name, value)
                # We stop the search here.
                return

        # If we are here, it means that property was not found.
        raise NoSuchPropertyError(property_path)

    @property
    def enabled(self):
        '''Return True if service is enabled.'''
        return self._proxy.getBoolean(
            self._section_name, self._prefix + '_enabled')

    @enabled.setter
    def enabled(self, value):
        '''Set value for enable.'''
        initial = self.enabled
        self._proxy.setBoolean(
            self._section_name, self._prefix + '_enabled', value)
        signal = Signal(
            self, initial_value=initial, current_value=self.enabled)
        self.notify('enabled', signal)
