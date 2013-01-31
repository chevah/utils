# -*- coding: utf-8 -*-
# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
"""
Test for configuration file.
"""
from __future__ import with_statement
import os
from StringIO import StringIO

from chevah.utils.testing import LogTestCase, manufacture
from chevah.utils.configuration_file import (
    ConfigurationFileMixin,
    FileConfigurationProxy,
    )
from chevah.utils.constants import CONFIGURATION_INHERIT
from chevah.utils.exceptions import ConfigurationError


class TestFileConfigurationProxy(LogTestCase):
    '''FileConfigurationProxy tests.'''

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
        with self.assertRaises(ConfigurationError) as context:
            config_file = StringIO()
            FileConfigurationProxy(
                configuration_path='some-path',
                configuration_file=config_file)
        self.assertEqual(1011, context.exception.id)

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
            with self.assertRaises(ConfigurationError) as context:
                FileConfigurationProxy(configuration_path=config_path)
            self.assertEqual(1012, context.exception.id)
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
        with self.assertRaises(ConfigurationError) as context:
            config.load()
        self.assertEqual(1002, context.exception.id)
        config_file.close()

    def test_getBoolean_bad_values(self):
        '''Test bad value for remote_admin_enabled.'''
        config_file = StringIO(
            '[section]\n'
            'bool_option = 3234\n')
        config = FileConfigurationProxy(configuration_file=config_file)
        config.load()
        with self.assertRaises(ConfigurationError) as context:
            config.getBoolean('section', 'bool_option')
        self.assertEqual(1000, context.exception.id)

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
        A string configuration can be set to a python string formating
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

    def _getConfig(self, content):
        config_file = StringIO(content)
        config = FileConfigurationProxy(
            configuration_file=config_file)
        config.load()
        return config

    def test_getIntegerOrNone_none(self):
        """
        Check getIntegerOrNone.
        """
        content = (
            u'[some_section]\n'
            u'some_none: Disabled\n'
            )

        config = self._getConfig(content=content)

        self.assertIsNone(
            config.getIntegerOrNone(u'some_section', u'some_none'))

    def test_getIntegerOrNone_int(self):
        """
        Check getIntegerOrNone.
        """
        content = (
            u'[some_section]\n'
            u'some_int: 7\n'
            )

        config = self._getConfig(content=content)

        self.assertEqual(
            7,
            config.getIntegerOrNone(u'some_section', u'some_int'))


class TestSection(object):
    '''A test section.'''

    def __init__(self, sign):
        self.property1 = u'value1-' + sign
        self.property2 = u'value2-' + sign

    def getAllProperties(self):
        return {
            'property1': self.property1,
            'property2': self.property2,
        }


class ConfigurationFileMixinUser(ConfigurationFileMixin):
    '''A test class using `ConfigurationFileMixin`.'''

    def __init__(self, configuration_path=None, configuration_file=None):
        self.checkConfigurationFileAndPathArguments(
            configuration_path, configuration_file)
        self._proxy = FileConfigurationProxy(
            configuration_path=configuration_path,
            configuration_file=configuration_file)
        self._proxy.load()
        self.section1 = TestSection(u'1')
        self.section2 = TestSection(u'2')

    @property
    def section_names(self):
        return [u'section1', u'section2']


class TestConfigurationFileMixin(LogTestCase):
    '''General tests for configuration file.'''

    def test_config_init_with_bad_arguments(self):
        """
        An error is raised at initialization if bad arguments are provided.
        """
        with self.assertRaises(AssertionError):
            ConfigurationFileMixinUser()
        with self.assertRaises(AssertionError):
            config_file = StringIO()
            ConfigurationFileMixinUser(
                configuration_path='some-path',
                configuration_file=config_file)

    def test_create_missing_sections_default(self):
        """
        When no section names are provied, createMissingSections will
        create default sections.
        """
        config_file = StringIO(u'[section3]\n')
        config = ConfigurationFileMixinUser(configuration_file=config_file)
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
        config = ConfigurationFileMixinUser(configuration_file=config_file)
        self.assertFalse(config._proxy.hasSection(u'section1'))
        self.assertFalse(config._proxy.hasSection(u'section2'))
        self.assertTrue(config._proxy.hasSection(u'section3'))
        config.createMissingSections([u'section1'])
        self.assertTrue(config._proxy.hasSection(u'section1'))
        self.assertFalse(config._proxy.hasSection(u'section2'))
        self.assertTrue(config._proxy.hasSection(u'section3'))

    def test_getAllProperties(self):
        """
        Check getting all properties.
        """
        config_file = StringIO(u'[section3]\n')
        config = ConfigurationFileMixinUser(configuration_file=config_file)
        props = config.getAllProperties()
        self.assertEqual(2, len(props))
        self.assertTrue(u'section1' in props)
        self.assertTrue(u'section2' in props)
        self.assertEqual(2, len(props['section1']))
        self.assertEqual(u'value1-1', props['section1']['property1'])
        self.assertEqual(u'value2-2', props['section2']['property2'])

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
                config = ConfigurationFileMixinUser(
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
                config = ConfigurationFileMixinUser(
                    configuration_path=config_path)
                self.assertEqual(
                    u'muță_value',
                    config._proxy.getString(
                        u'another_muță',
                        u'another_muță_option'))
        finally:
            if test_segments:
                test_filesystem.deleteFile(test_segments, ignore_errors=True)
