# -*- coding: utf-8 -*-
# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
"""
Test for configuration file.
"""
from __future__ import with_statement
import os
from StringIO import StringIO

from zope.interface import implements

from chevah.utils.testing import manufacture, UtilsTestCase
from chevah.utils.configuration_file import (
    ConfigurationFileMixin,
    ConfigurationSectionMixin,
    FileConfigurationProxy,
    )
from chevah.utils.constants import CONFIGURATION_INHERIT
from chevah.utils.exceptions import (
    NoSuchPropertyError,
    NoSuchSectionError,
    ReadOnlyPropertyError,
    UtilsError,
    )
from chevah.utils.interfaces import (
    Attribute,
    Interface,
    PublicAttribute,
    PublicWritableAttribute,
    )


class TestFileConfigurationProxy(UtilsTestCase):
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

    def test_getBoolean_bad_values(self):
        '''Test bad value for remote_admin_enabled.'''
        config_file = StringIO(
            '[section]\n'
            'bool_option = 3234\n')
        config = FileConfigurationProxy(configuration_file=config_file)
        config.load()
        with self.assertRaises(UtilsError) as context:
            config.getBoolean('section', 'bool_option')
        self.assertEqual(u'1000', context.exception.event_id)

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


class IDummySection(Interface):
    """
    Interface for IDummySection.
    """

    hidden_property = Attribute('Some attribute which is not exposed')
    enabled = PublicWritableAttribute('Public attribute')
    property1 = PublicWritableAttribute('Public attribute')
    property2 = PublicAttribute('Public attribute in read only')

    def some_method():
        """
        Just for test.
        """


class MissingPropertyConfigurationSection(ConfigurationSectionMixin):
    """
    A configurarion section used for testing properties behavior
    when property is not defined.
    """

    implements(IDummySection)

    def __init__(self):
        pass


class DummyConfigurationSection(ConfigurationSectionMixin):
    """
    A dummy configuration section used to help with testing.
    """

    implements(IDummySection)

    _section_name = 'section1'
    _prefix = 'sec'

    def __init__(self, sign='sign', proxy=None):
        if proxy is None:
            self._proxy = manufacture.makeFileConfigurationProxy(
                content='[section1]\nsec_enabled: True\n')
        else:
            self._proxy = proxy
        self.property1 = u'value1-' + sign
        self.property2 = u'value2-' + sign
        self.hiden_property = u'value3-' + sign

    def some_method(self):
        """
        Here, just to create trouble.
        """
        return


class TestConfigurationSectionMixin(UtilsTestCase):
    """
    Test for ConfigurationSectionMixin.
    """

    def setUp(self):
        super(TestConfigurationSectionMixin, self).setUp()
        self.config = DummyConfigurationSection()

    def test_getAllProperties_good(self):
        """
        All public properties are exported without a prefix.
        """
        result = self.config.getAllProperties()

        self.assertEqual(3, len(result))
        self.assertFalse('hiden_property' in result)
        self.assertTrue(result['enabled'])
        self.assertEqual(u'value1-sign', result['property1'])
        self.assertEqual(u'value2-sign', result['property2'])

    def test_getAllProperties_missing_properties(self):
        """
        An error is raised if the interface defines an public attribute
        which is not defined in the object.
        """
        self.config = MissingPropertyConfigurationSection()

        with self.assertRaises(NoSuchPropertyError) as context:
            self.config.getAllProperties()

        self.assertEqual(
            'No such property property1', context.exception.message)

    def test_enabled(self):
        """
        Enabled property is provided by the Mixin and it also emits
        signals on change.
        """
        call_list = []

        def notification(signal):
            call_list.append(signal)

        self.config.subscribe('enabled', notification)
        self.config.enabled = True
        self.assertIsTrue(self.config.enabled)

        self.config.enabled = False
        self.assertIsFalse(self.config.enabled)

        self.assertEqual(2, len(call_list))
        signal = call_list[1]
        self.assertIsTrue(signal.initial_value)
        self.assertIsFalse(signal.current_value)
        self.assertEqual(self.config, signal.source)

    def test_setProperty_with_parent(self):
        """
        An error is raise if property_path still have a parent.
        """
        with self.assertRaises(NoSuchPropertyError) as context:
            self.config.setProperty('property1/child', 'something')

        self.assertExceptionID(u'1032', context.exception)

    def test_setProperty_non_existent(self):
        """
        An error is raise if property_path does not existes.
        """
        with self.assertRaises(NoSuchPropertyError) as context:
            self.config.setProperty('property_non_existent', 'something')

        self.assertExceptionID(u'1032', context.exception)

    def test_setProperty_read_only(self):
        """
        An error is raised when trying to write a read only property.
        """
        with self.assertRaises(ReadOnlyPropertyError) as context:
            self.config.setProperty('property2', 'something')

        self.assertExceptionID(u'1034', context.exception)

    def test_setProperty_defined_but_non_exitent(self):
        """
        An error is raised if property is defined on the interface, but
        not existent on the object.
        """
        self.config = MissingPropertyConfigurationSection()

        with self.assertRaises(NoSuchPropertyError):
            self.config.setProperty('property1', 'something')

    def test_setProperty_ok(self):
        """
        Value is set of property exists..
        """
        self.config.setProperty('property1', 'something')

        self.assertEqual('something', self.config.property1)


class DummyConfigurationFileMixin(ConfigurationFileMixin):
    '''A test class using `ConfigurationFileMixin`.'''

    def __init__(self, configuration_path=None, configuration_file=None):
        self.checkConfigurationFileAndPathArguments(
            configuration_path, configuration_file)
        self._proxy = FileConfigurationProxy(
            configuration_path=configuration_path,
            configuration_file=configuration_file)
        self._proxy.load()
        self.section1 = DummyConfigurationSection(
            sign=u'1', proxy=self._proxy)
        self.section2 = DummyConfigurationSection(
            sign=u'2', proxy=self._proxy)

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
        When no section names are provied, createMissingSections will
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

    def test_getAllProperties(self):
        """
        All properties from all sections are returned, expecting hidden
        properties.
        """
        config_file = StringIO(
            u'[section1]\n'
            u'sec_enabled: True\n'
            u'[section2]\n'
            u'sec_enabled: True\n'
            )
        config = DummyConfigurationFileMixin(configuration_file=config_file)

        props = config.getAllProperties()

        self.assertEqual(2, len(props))
        self.assertTrue(u'section1' in props)
        self.assertTrue(u'section2' in props)

        self.assertEqual(3, len(props['section1']))
        self.assertEqual(True, props['section1']['enabled'])
        self.assertEqual(u'value1-1', props['section1']['property1'])
        self.assertEqual(u'value2-1', props['section1']['property2'])

    def test_setProperties_final_property(self):
        """
        An error is raised when trying to set a final property which
        has no section.
        """
        config = DummyConfigurationFileMixin(configuration_file=StringIO())

        with self.assertRaises(NoSuchPropertyError):
            config.setProperty('section1', 'something')

    def test_setProperties_unknown_section(self):
        """
        An error is raised when trying to set a property forn an unknown
        section.
        """
        config = DummyConfigurationFileMixin(configuration_file=StringIO())

        with self.assertRaises(NoSuchSectionError) as context:
            config.setProperty('no_such_section/property', 'something')

        self.assertExceptionID(u'1033', context.exception)

    def test_setProperties_unknown_property(self):
        """
        An error is raised when trying to set an unknown property for a
        valid section.
        """
        config = DummyConfigurationFileMixin(configuration_file=StringIO())

        with self.assertRaises(NoSuchPropertyError):
            config.setProperty('section1/unknown_property', 'something')

    def test_setProperties_ok_attribute(self):
        """
        Value is set if section and property exists and property is
        a direct attribute.
        """
        config = DummyConfigurationFileMixin(configuration_file=StringIO())
        value = manufacture.getUniqueString()

        config.setProperty('section1/property1', value)

        self.assertEqual(value, config.section1.property1)

    def test_setProperties_ok_property(self):
        """
        Value is set even if property is defiend using @property decorator.
        """
        content = (
            '[section1]\n'
            'sec_enabled: True\n'
            )
        config = DummyConfigurationFileMixin(
            configuration_file=StringIO(content))
        self.assertIsTrue(config.section1.enabled)

        config.setProperty('section1/enabled', False)

        self.assertIsFalse(config.section1.enabled)

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
