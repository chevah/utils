# -*- coding: utf-8 -*-
# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
"""
Test for configuration file.
"""
from __future__ import with_statement
import os
from StringIO import StringIO

from chevah.utils.testing import manufacture, UtilsTestCase
from chevah.utils.configuration import ConfigurationSectionMixin
from chevah.utils.configuration_file import (
    ConfigurationFileMixin,
    FileConfigurationProxy,
    )
from chevah.utils.constants import CONFIGURATION_INHERIT
from chevah.utils.exceptions import (
    UtilsError,
    )


class TestFileConfigurationProxy(UtilsTestCase):
    '''FileConfigurationProxy tests.'''

    special_characters = u'~`!@#$%^&*()_\\/-+="\''

    def makeFileConfiguration(self, content):
        """
        Returns a file configuration with `content`.
        """
        config_file = StringIO(content)
        config = FileConfigurationProxy(configuration_file=config_file)
        config.load()
        return config

    def makeIntegerFileConfiguration(self, value):
        """
        Returns a test configuration file with an integer `value`.
        """
        template = (
            u'[section]\n'
            u'integer: %d\n'
            )
        content = template % value
        return self.makeFileConfiguration(content)

    def test_init_with_no_arguments(self):
        """
        An error is raised when initializing with no arguments.
        """
        with self.assertRaises(AssertionError):
            FileConfigurationProxy()

    def test_init_with_bad_path(self):
        """
        An error is raised when initialized with a bad path.
        """
        with self.assertRaises(UtilsError) as context:
            config_file = StringIO()
            FileConfigurationProxy(
                configuration_path='some-path',
                configuration_file=config_file)
        self.assertEqual(u'1011', context.exception.event_id)

    def test_init_no_read_to_config_file(self):
        '''Test loading a configuration file with no read permissions.'''
        # XXX:62
        # This should be make a generic test when we have a API for changing
        # file permissions on Windows.
        if os.name != 'posix':
            raise self.skipTest()

        test_filesystem = manufacture.fs
        test_segments = None
        config_path = None
        try:
            test_segments = test_filesystem.createFileInTemp(content='')
            config_path = test_filesystem.getRealPathFromSegments(
                test_segments)
            test_filesystem.setAttributes(
                test_segments, {'permissions': 0})
            with self.assertRaises(UtilsError) as context:
                FileConfigurationProxy(configuration_path=config_path)
            self.assertEqual(u'1012', context.exception.event_id)
        finally:
            test_filesystem.setAttributes(
                test_segments, {'permissions': 0777})
            test_filesystem.deleteFile(test_segments, ignore_errors=True)

    def test_load_unicode_file(self):
        """
        System test for loading unicode data.
        """
        config_content = (
            u'[another_muță]\n'
            u'another_muță_option: another_muță_value\n'
            u'[some_section]\n'
            u'some_section_option: some_section_value\n'
            u'')
        test_filesystem = manufacture.fs
        test_segments = None
        try:
            test_segments = test_filesystem.createFileInTemp(
                content=config_content)
            config_path = test_filesystem.getRealPathFromSegments(
                test_segments)
            with test_filesystem._impersonateUser():
                config = FileConfigurationProxy(
                    configuration_path=config_path)
                config.load()
                sections = config.sections
                self.assertEqual(2, len(sections))
                self.assertTrue(isinstance(sections[0], unicode))
                self.assertTrue(u'another_muță' in sections)
                self.assertTrue(u'some_section' in sections)
                self.assertEqual(
                    u'another_muță_value',
                    config.getString(
                        u'another_muță',
                        u'another_muță_option'))
        finally:
            if test_segments:
                test_filesystem.deleteFile(test_segments, ignore_errors=True)

    def test_load_file(self):
        """
        Check loading settings from a file.
        """
        config_file = StringIO(
            u'[another_muță]')
        config = FileConfigurationProxy(
            configuration_file=config_file)
        self.assertEqual([], config.sections)
        config.load()
        self.assertEqual(u'another_muță', config.sections[0])

    def test_save(self):
        """
        System test for persisting changes into a file.
        """
        config_content = (
            u'[another_muță]\n'
            u'another_muță_option: another_muță_value\n\n')
        test_filesystem = manufacture.fs
        test_segments = None
        try:
            test_segments = test_filesystem.createFileInTemp(
                content=config_content)
            config_path = test_filesystem.getRealPathFromSegments(
                test_segments)
            with test_filesystem._impersonateUser():
                config = FileConfigurationProxy(
                    configuration_path=config_path)
                config.load()
                self.assertEqual(
                    u'another_muță_value',
                    config.getString(
                        u'another_muță',
                        u'another_muță_option'))
                config.setString(
                        u'another_muță',
                        u'another_muță_option',
                        u'muță_value',
                        )
                config.save()
                config = FileConfigurationProxy(
                    configuration_path=config_path)
                config.load()
                self.assertEqual(
                    u'muță_value',
                    config.getString(
                        u'another_muță',
                        u'another_muță_option'))
        finally:
            if test_segments:
                test_filesystem.deleteFile(test_segments, ignore_errors=True)

    def test_sections(self):
        """
        Check sections property.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'[another_muță]\n'
            u'[yet_another]\n'
            u'some_value: 3\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        sections = config.sections
        self.assertEqual(3, len(sections))
        self.assertTrue(u'some_section' in sections)
        self.assertTrue(u'another_muță' in sections)
        self.assertTrue(u'yet_another' in sections)

    def test_add_section(self):
        """
        Check adding a section.
        """
        config_file = StringIO(
            u'[another_muță]\n'
            u'some_value: 3\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertEqual(1, len(config.sections))
        config.addSection(u'another_muță2')
        self.assertEqual(2, len(config.sections))
        self.assertTrue(u'another_muță2' in config.sections)

    def test_remove_section(self):
        """
        Check removing a section.
        """
        section_name = u'another_muță'
        config_file = StringIO((
            u'[%s]\n'
            u'some_value: 3\n'
            u''
            ) % (section_name))
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertTrue(config.hasSection(section_name))

        config.removeSection(section_name)

        self.assertFalse(config.hasSection(section_name))

    def test_hasSection(self):
        """
        Check hasSection.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'[another_muță]\n'
            u'some_value: 3\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertTrue(config.hasSection(u'some_section'))
        self.assertTrue(config.hasSection(u'another_muță'))

    def test_hasOption(self):
        """
        Check hasOption.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'[another_muță]\n'
            u'some_value: 3\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertTrue(
            config.hasOption(u'another_muță', u'some_value'))
        self.assertFalse(
            config.hasOption(u'some_section', u'some_value'))

    def test_bad_section_header(self):
        """
        An error is raised if a section name is bad formated.
        """
        config_file = StringIO(
            '[section\n'
            'new_option: value\n'
            '[remote_admin]\n'
            'remote_admin_enabled: No\n')
        config = FileConfigurationProxy(configuration_file=config_file)
        with self.assertRaises(UtilsError) as context:
            config.load()
        self.assertEqual(u'1002', context.exception.event_id)
        config_file.close()

    def test_getString(self):
        """
        Check getString.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'some_value:  maca   \n'
            u'[another_muță]\n'
            u'some_value: raca\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertEqual(
            u'maca',
            config.getString(u'some_section', u'some_value'))
        self.assertEqual(
            u'raca',
            config.getString(u'another_muță', u'some_value'))

    def test_getString_quotes(self):
        """
        String values may be quoted.
        """
        config_file = StringIO(
            u'[section]\n'
            u'no_quote: \'maca" \n'
            u'single_quote: \'maca\' \n'
            u'double_quote: "maca" \n'
            u'multiple_single_quote: \'\'maca\'\' \n'
            u'multiple_double_quote: ""maca"" \n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertEqual(
            u'\'maca"',
            config.getString(u'section', u'no_quote'))
        self.assertEqual(
            u'maca',
            config.getString(u'section', u'single_quote'))
        self.assertEqual(
            u'maca',
            config.getString(u'section', u'double_quote'))
        self.assertEqual(
            u'\'maca\'',
            config.getString(u'section', u'multiple_single_quote'))
        self.assertEqual(
            u'"maca"',
            config.getString(u'section', u'multiple_double_quote'))

    def test_getString_with_python_formating(self):
        """
        A string configuration can hold a python string formating
        expressions.
        """
        config_file = StringIO(
            u'[section]\n'
            u'value: do %(some)s value\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertEqual(
            u'do %(some)s value',
            config.getString(u'section', u'value'))

    def test_setString_with_python_formating(self):
        """
        A string configuration can be set to a python string formatting
        expressions.
        """
        config_file = StringIO(
            u'[section]\n'
            u'value: value\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()

        config.setString(u'section', u'value', u'do %(some)s value')

        self.assertEqual(
            u'do %(some)s value',
            config.getString(u'section', u'value'))

    def test_getString_with_wild_charactes(self):
        """
        A string configuration can hold any character and it does not
        require any special escaping.
        """
        config_file = StringIO((
            u'[section]\n'
            u'value: %s\n'
            u'') % (self.special_characters)
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        self.assertEqual(
            self.special_characters,
            config.getString(u'section', u'value'))

    def test_setString_with_wild_charactes(self):
        """
        A string configuration can be set to text containing any characters.
        """
        config_file = StringIO(
            u'[section]\n'
            u'value: value\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()

        config.setString(u'section', u'value', self.special_characters)

        self.assertEqual(
            self.special_characters,
            config.getString(u'section', u'value'))

    def test_isDisabledValue(self):
        """
        Return `True` if value is one of the disabled values or `False`
        otherwise.
        """
        config = FileConfigurationProxy(configuration_file=StringIO())

        self.assertFalse(config.isDisabledValue(u'some-value'))

        self.assertTrue(config.isDisabledValue('disable'))
        self.assertTrue(config.isDisabledValue('Disable'))
        self.assertTrue(config.isDisabledValue('disabled'))

    def check_getStringOrNone(self, getter_name):
        """
        Helper for retrieving strings which can be disabled.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'some_none:  None   \n'
            u'some_disable: disable\n'
            u'some_disabled: DiSabled\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        getter = getattr(config, getter_name)
        self.assertIsNone(getter(u'some_section', u'some_none'))
        self.assertIsNone(getter(u'some_section', u'some_disable'))
        self.assertIsNone(getter(u'some_section', u'some_disabled'))

    def test_getStringOrNone(self):
        """
        "None" or "Disabled" values will be returned as `None` object.
        """
        self.check_getStringOrNone("getStringOrNone")

    def check_setStringOrNone(self, getter_name, setter_name):
        """
        Helper for testing string values which can be disabled.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'some_none: something\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        getter = getattr(config, getter_name)
        setter = getattr(config, setter_name)

        self.assertEqual(
            u'something',
            getter(u'some_section', u'some_none'))

        setter(u'some_section', u'some_none', None)
        self.assertIsNone(
            getter(u'some_section', u'some_none'))

        setter(u'some_section', u'some_none', 'None')
        self.assertIsNone(
            getter(u'some_section', u'some_none'))

    def test_setStringOrNone(self):
        """
        Tests string values which can be disabled.
        """
        self.check_setStringOrNone("getStringOrNone", "setStringOrNone")

    def check_getStringOrInherit(self, getter_name):
        """
        Helper for getting inheritable strings.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'some_none: Inherit   \n'
            u'some_disable: inherited\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()

        getter = getattr(config, getter_name)
        self.assertEqual(
            CONFIGURATION_INHERIT[0],
            getter(u'some_section', u'some_none'))
        self.assertEqual(
            CONFIGURATION_INHERIT[0],
            getter(u'some_section', u'some_disable'))

    def test_getStringOrInherit(self):
        """
        When any of the "inherit" meta values is retrieved, it will alwasy
        be retrieved as lower case for first CONFIGURATION_INHERIT.
        """
        self.check_getStringOrInherit("getStringOrInherit")

    def check_setStringOrInherit(self, getter_name, setter_name):
        """
        Helper for setting string values which can be disabled.
        """
        config_file = StringIO(
            u'[some_section]\n'
            u'some_none: something\n'
            u'',
            )
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        getter = getattr(config, getter_name)
        setter = getattr(config, setter_name)
        self.assertEqual(
            u'something',
            getter(u'some_section', u'some_none'))
        setter(
            u'some_section', u'some_none', CONFIGURATION_INHERIT[0].upper())
        self.assertEqual(
            CONFIGURATION_INHERIT[0],
            getter(u'some_section', u'some_none'))

        setter(
            u'some_section', u'some_none', CONFIGURATION_INHERIT[1])
        self.assertEqual(
            CONFIGURATION_INHERIT[0],
            getter(u'some_section', u'some_none'))

    def test_setStringOrInherit(self):
        """
        When any of the possible inherited meta values is set, it will always
        be written as lower values.
        """
        self.check_setStringOrInherit(
            getter_name="getStringOrInherit",
            setter_name="setStringOrInherit",
            )

    def test_getStringSpecial(self):
        """
        Test for retrieving special values.

        This is a group of all other tests
        """
        self.check_getStringOrNone("getStringSpecial")
        self.check_getStringOrInherit("getStringSpecial")

    def test_setStringSpecial(self):
        """
        Test for getting special values.

        This is a group of all other tests
        """
        self.check_setStringOrNone(
            "getStringSpecial", "setStringSpecial")
        self.check_setStringOrInherit(
            "getStringSpecial", "setStringSpecial")

    def test_getIntegerOrNone_none(self):
        """
        Check getIntegerOrNone.
        """
        content = (
            u'[some_section]\n'
            u'some_none: Disabled\n'
            )

        config = self.makeFileConfiguration(content=content)

        self.assertIsNone(
            config.getIntegerOrNone(u'some_section', u'some_none'))

    def test_getIntegerOrNone_int(self):
        """
        Check getIntegerOrNone.
        """
        config = self.makeIntegerFileConfiguration(7)

        self.assertEqual(
            7, config.getIntegerOrNone(u'section', u'integer'))

    def test_setInteger_int(self):
        """
        Set integer can be used for directly setting an integer number.
        """
        config = self.makeIntegerFileConfiguration(7)

        config.setInteger('section', u'integer', 10)

        self.assertEqual(10, config.getInteger(u'section', u'integer'))

    def test_setInteger_bad_value(self):
        """
        When setting an integer to an invalid value, an error is raised and
        the previous value is kept.
        """
        config = self.makeIntegerFileConfiguration(7)

        with self.assertRaises(UtilsError) as context:
            config.setInteger('section', u'integer', 'bad-value')

        self.assertExceptionID(u'1001', context.exception)
        self.assertContains('integer value', context.exception.message)
        self.assertEqual(7, config.getInteger(u'section', u'integer'))

    def test_setInteger_float(self):
        """
        Float values are floor rounded to integers.
        """
        config = self.makeIntegerFileConfiguration(7)

        config.setInteger('section', u'integer', 100.6)

        self.assertEqual(100, config.getInteger(u'section', u'integer'))

    def test_getBoolean_valid(self):
        """
        A boolean value is read if stored in human readable boolean.
        """
        content = (
            '[section]\n'
            'bool_option: YeS\n')
        config = self.makeFileConfiguration(content=content)

        self.assertTrue(config.getBoolean('section', 'bool_option'))

    def test_getBoolean_invalid(self):
        """
        An error is raised when trying to rad an invalid boolean value.
        """
        content = (
            '[section]\n'
            'bool_option = 3234\n')
        config = self.makeFileConfiguration(content=content)

        with self.assertRaises(UtilsError) as context:
            config.getBoolean('section', 'bool_option')

        self.assertEqual(u'1000', context.exception.event_id)

    def test_setBoolean_valid(self):
        """
        It can set a boolean value specified as free form.
        """
        content = (
            u'[some_section]\n'
            u'some_boolean: yes\n'
            )
        config = self.makeFileConfiguration(content=content)

        config.setBoolean('some_section', u'some_boolean', 'No')
        self.assertFalse(config.getBoolean(u'some_section', u'some_boolean'))

        config.setBoolean('some_section', u'some_boolean', True)
        self.assertTrue(config.getBoolean(u'some_section', u'some_boolean'))

    def test_setBoolean_invalid(self):
        """
        When an invalid boolean value is set, the old value is kept and a
        error is raised.
        """
        content = (
            u'[some_section]\n'
            u'some_boolean: yes\n'
            )
        config = self.makeFileConfiguration(content=content)

        with self.assertRaises(UtilsError) as context:
            config.setBoolean('some_section', u'some_boolean', 'bad-value')

        self.assertExceptionID(u'1001', context.exception)
        self.assertContains('boolean value', context.exception.message)
        self.assertTrue(config.getBoolean(u'some_section', u'some_boolean'))

    def test_setBooleanInherit_valid(self):
        """
        It can set a boolean value or the special inherit value.
        """
        content = (
            u'[some_section]\n'
            u'some_boolean: yes\n'
            )
        config = self.makeFileConfiguration(content=content)

        config.setBooleanOrInherit('some_section', u'some_boolean', False)
        self.assertFalse(
            config.getBooleanOrInherit(u'some_section', u'some_boolean'))

        config.setBooleanOrInherit('some_section', u'some_boolean', 'YeS')
        self.assertTrue(
            config.getBooleanOrInherit(u'some_section', u'some_boolean'))

        config.setBooleanOrInherit(
            'some_section', u'some_boolean', CONFIGURATION_INHERIT[0])
        self.assertEqual(
            CONFIGURATION_INHERIT[0],
            config.getBooleanOrInherit(u'some_section', u'some_boolean'),
            )

    def test_booleanConverter_valid(self):
        """
        Convert free from boolean into standard pyton boolean values.
        """
        config = self.makeFileConfiguration(content='')

        for value in [True, 1, '1', 'tRuE', 'yEs']:
            self.assertTrue(config._booleanConverter(value))

        for value in [False, 0, '0', 'falSE', 'nO']:
            self.assertFalse(config._booleanConverter(value))

    def test_booleanConverter_invalid(self):
        """
        An error is raised when value can not be converted.
        """
        config = self.makeFileConfiguration(content='')

        with self.assertRaises(ValueError):
            config._booleanConverter('no-boolean')

        with self.assertRaises(ValueError):
            config._booleanConverter(object())

        with self.assertRaises(ValueError):
            config._booleanConverter(4)

    def test_getFload_valid(self):
        """
        A float value is can be read.
        """
        content = (
            '[section]\n'
            'float_option: 1.43\n')
        config = self.makeFileConfiguration(content=content)

        self.assertEqual(1.43, config.getFloat('section', 'float_option'))

    def test_getFload_invalid(self):
        """
        An error is raised when value is not float.
        """
        content = (
            '[section]\n'
            'float_option: bla\n')
        config = self.makeFileConfiguration(content=content)

        with self.assertRaises(UtilsError) as context:
            config.getFloat('section', 'float_option')

        self.assertExceptionID(u'1000', context.exception)
        self.assertContains(
            'floating number value', context.exception.message)

    def test_setFload_valid(self):
        """
        A float value is can be set as float, integer or string.
        """
        content = (
            '[section]\n'
            'float_option: 0\n')
        config = self.makeFileConfiguration(content=content)

        config.setFloat('section', 'float_option', 2.45)
        self.assertEqual(2.45, config.getFloat('section', 'float_option'))

        config.setFloat('section', 'float_option', 2)
        result = config.getFloat('section', 'float_option')
        self.assertEqual(2.0, result)
        self.assertIsInstance(float, result)

        config.setFloat('section', 'float_option', u'3.45')
        self.assertEqual(3.45, config.getFloat('section', 'float_option'))

    def test_setFload_invalid(self):
        """
        When setting an invalid float value, error is raised and previous
        value is kept.
        """
        content = (
            '[section]\n'
            'float_option: 2.34\n')
        config = self.makeFileConfiguration(content=content)

        with self.assertRaises(UtilsError) as context:
            config.setFloat('section', 'float_option', 'bad-value')

        self.assertExceptionID(u'1001', context.exception)
        self.assertContains(
            'floating number value', context.exception.message)
        self.assertEqual(2.34, config.getFloat('section', 'float_option'))


class DummyConfigurationFileMixin(ConfigurationFileMixin):
    """
    A test class implementing `ConfigurationFileMixin`.
    """

    class DummyConfigurationSection(ConfigurationSectionMixin):
        """
        A dummy configuration section used to help with testing.
        """

        _section_name = 'section1'
        _prefix = 'sec'

        def __init__(self, sign='sign'):
            self.property1 = u'value1-' + sign
            self.property2 = u'value2-' + sign
            self.hiden_property = u'value3-' + sign

    def __init__(self, configuration_path=None, configuration_file=None):
        self.checkConfigurationFileAndPathArguments(
            configuration_path, configuration_file)
        self._proxy = FileConfigurationProxy(
            configuration_path=configuration_path,
            configuration_file=configuration_file)
        self._proxy.load()
        self.section1 = self.DummyConfigurationSection(sign=u'1')
        self.section2 = self.DummyConfigurationSection(sign=u'2')

    @property
    def section_names(self):
        return [u'section1', u'section2']


class TestConfigurationFileMixin(UtilsTestCase):
    """
    Tests for ConfigurationFileMixin.
    """

    def test_config_init_with_bad_arguments(self):
        """
        An error is raised at initialization if bad arguments are provided.
        """
        with self.assertRaises(AssertionError):
            DummyConfigurationFileMixin()
        with self.assertRaises(AssertionError):
            config_file = StringIO()
            DummyConfigurationFileMixin(
                configuration_path='some-path',
                configuration_file=config_file)

    def test_create_missing_sections_default(self):
        """
        When no section names are provided, createMissingSections will
        create default sections.
        """
        config_file = StringIO(u'[section3]\n')
        config = DummyConfigurationFileMixin(configuration_file=config_file)
        self.assertFalse(config._proxy.hasSection(u'section1'))
        self.assertFalse(config._proxy.hasSection(u'section2'))
        self.assertTrue(config._proxy.hasSection(u'section3'))
        config.createMissingSections()
        self.assertTrue(config._proxy.hasSection(u'section1'))
        self.assertTrue(config._proxy.hasSection(u'section2'))
        self.assertTrue(config._proxy.hasSection(u'section3'))

    def test_create_missing_sections_list(self):
        """
        When section names are provied, createMissingSections will
        create only those sections.
        """
        config_file = StringIO(u'[section3]\n')
        config = DummyConfigurationFileMixin(configuration_file=config_file)
        self.assertFalse(config._proxy.hasSection(u'section1'))
        self.assertFalse(config._proxy.hasSection(u'section2'))
        self.assertTrue(config._proxy.hasSection(u'section3'))
        config.createMissingSections([u'section1'])
        self.assertTrue(config._proxy.hasSection(u'section1'))
        self.assertFalse(config._proxy.hasSection(u'section2'))
        self.assertTrue(config._proxy.hasSection(u'section3'))

    def test_save(self):
        """
        System test for saving configuration.
        """
        config_content = (
            u'[another_muță]\n'
            u'another_muță_option: another_muță_value\n'
            u'[some_section]\n'
            u'some_section_option: some_section_value\n'
            u'')
        test_filesystem = manufacture.fs
        test_segments = None
        try:
            test_segments = test_filesystem.createFileInTemp(
                content=config_content)
            config_path = test_filesystem.getRealPathFromSegments(
                test_segments)
            with test_filesystem._impersonateUser():
                config = DummyConfigurationFileMixin(
                    configuration_path=config_path)
                self.assertEqual(
                    u'another_muță_value',
                    config._proxy.getString(
                        u'another_muță',
                        u'another_muță_option'))

                config._proxy.setString(
                        u'another_muță',
                        u'another_muță_option',
                        u'muță_value',
                        )
                config.save()
                config = DummyConfigurationFileMixin(
                    configuration_path=config_path)
                self.assertEqual(
                    u'muță_value',
                    config._proxy.getString(
                        u'another_muță',
                        u'another_muță_option'))
        finally:
            if test_segments:
                test_filesystem.deleteFile(test_segments, ignore_errors=True)
