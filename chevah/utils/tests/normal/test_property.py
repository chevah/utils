# Copyright (c) 2011-2013 Adi Roiban.
# See LICENSE for details.
"""
Test for property handling.
"""
from __future__ import with_statement

from zope.interface import implements

from chevah.utils.testing import manufacture, UtilsTestCase
from chevah.utils.property import (
    PropertyMixin,
    )
from chevah.utils.exceptions import (
    NoSuchAttributeError,
    NoSuchSectionError,
    )
from chevah.utils.interfaces import (
    Attribute,
    IPropertyMixin,
    Interface,
    PublicAttribute,
    PublicSectionAttribute,
    PublicWritableAttribute,
    )


class IDummyNodeSection(Interface):
    """
    Interface for node section.
    """

    prop_section = PublicSectionAttribute('A section')
    prop_section_normal = Attribute('An section which is not exposed')
    prop_node_rw = PublicWritableAttribute('Public attribute')
    prop_node_ro = PublicAttribute('Public attribute in read only')
    prop_node1_ro = PublicAttribute('Public attribute 2 in read only')
    prop_node_normal = Attribute('An attribute which is not exposed')

    def other_method():
        """
        Just for test.
        """


class IDummyLeafSection(IPropertyMixin):
    """
    Interface for top level section.
    """

    prop_normal = Attribute('Some attribute which is not exposed')
    prop_rw = PublicWritableAttribute('Public attribute')
    prop_ro = PublicAttribute('Public attribute in read only')
    prop_wrapped = PublicWritableAttribute(
        'Public attribute wrapped in a decorator.')

    def some_method():
        """
        Just for test.
        """


class DummyLeafConfigurationSection(PropertyMixin):
    """
    A dummy configuration section used to help with testing.
    It has no sections.
    """

    implements(IDummyLeafSection)

    _section_name = 'section1'
    _prefix = 'sec'

    def __init__(self):
        self._parent = None
        self._proxy = manufacture.makeFileConfigurationProxy(
            content='[section1]\n\n')
        self.prop_normal = u'prop_normal'
        self.prop_ro = u'prop_ro'
        self.prop_rw = u'prop_rw'
        self._prop_wrapped = u'prop_wrapped'

    @property
    def prop_wrapped(self):
        """
        A property wrapped using property decorator.
        """
        return self._prop_wrapped

    @prop_wrapped.setter
    def prop_wrapped(self, value):
        self._prop_wrapped = value

    def some_method(self):
        """
        Here, just to create trouble.
        """
        return


class MissingPropertyConfigurationSection(PropertyMixin):
    """
    A configuration section used for testing properties behavior
    when properties are not implemented.
    """

    implements(IDummyNodeSection)

    def __init__(self):
        self.prop_section = DummyLeafConfigurationSection()


class MissingSectionConfigurationSection(PropertyMixin):
    """
    A configuration section used for testing section behavior
    when section is not implemented.
    """

    implements(IDummyNodeSection)

    def __init__(self):
        self.prop_node_normal = u'prop_node_normal'
        self.prop_node_ro = u'prop_node_ro'
        self.prop_node1_ro = u'prop_node1_ro'
        self.prop_node_rw = u'prop_node_rw'


class DummyNodeConfigurationSection(PropertyMixin):
    """
    A dummy configuration section used to help with testing.
    It contains properties and sections.
    """

    implements(IDummyNodeSection)

    def __init__(self):
        # _proxy is here for ConfigurationSection
        self._proxy = None
        self._parent = None
        self.prop_section = DummyLeafConfigurationSection()
        self.prop_section_normal = DummyLeafConfigurationSection()
        self.prop_node_normal = u'prop_node_normal'
        self.prop_node_ro = u'prop_node_ro'
        self.prop_node1_ro = u'prop_node1_ro'
        self.prop_node_rw = u'prop_node_rw'


class TestPropertyMixin(UtilsTestCase):
    """
    Tests for PropertyMixin.
    """

    def setUp(self):
        super(TestPropertyMixin, self).setUp()
        self.config = DummyNodeConfigurationSection()

    def test_interface(self):
        """
        Check that interface defintion is ok.
        """
        self.assertProvides(IPropertyMixin, self.config)

    def test_traversePath(self):
        """
        traversePath will parse the property_path and return head and tail.
        """

        self.assertEqual((None, None), self.config.traversePath(None))
        self.assertEqual((None, None), self.config.traversePath(''))
        self.assertEqual(('bla', None), self.config.traversePath('bla'))
        self.assertEqual(('bla', None), self.config.traversePath('bla/'))
        self.assertEqual(('bla', 'tra'), self.config.traversePath('bla/tra'))
        self.assertEqual(('bl', 'tra/'), self.config.traversePath('bl/tra/'))

    def test_getProperty_root_no_branch(self):
        """
        All public properties are exported for a top level section.
        """
        result = self.config.prop_section.getProperty()

        self.assertEqual(3, len(result))
        self.assertFalse('prop_normal' in result)
        self.assertEqual(u'prop_ro', result['prop_ro'])
        self.assertEqual(u'prop_rw', result['prop_rw'])
        self.assertEqual(u'prop_wrapped', result['prop_wrapped'])

    def test_getProperty_with_branches(self):
        """
        All public properties are exported for a node with attached
        properties and sub sections.
        """
        result = self.config.getProperty()

        self.assertEqual(4, len(result))
        self.assertFalse('prop_section_normal' in result)
        # We don't check all properties for prop_section, since this is
        # done in another tests.
        self.assertIsNotNone(result['prop_section'])

        self.assertEqual(u'prop_node1_ro', result['prop_node1_ro'])
        self.assertEqual(u'prop_node_ro', result['prop_node_ro'])
        self.assertEqual(u'prop_node_rw', result['prop_node_rw'])

    def test_getProperty_missing_properties(self):
        """
        An error is raised if the interface defines an public attribute
        which is not defined in the object.
        """
        self.config = MissingPropertyConfigurationSection()

        with self.assertRaises(NoSuchAttributeError) as context:
            self.config.getProperty()

        self.assertExceptionID(u'1032', context.exception)
        self.assertEqual(
            'No such property prop_node_rw',
            context.exception.message)

    def test_getProperty_missing_section(self):
        """
        An error is raised if the interface defines an public section
        which is not defined in the object.
        """
        self.config = MissingSectionConfigurationSection()

        with self.assertRaises(NoSuchSectionError) as context:
            self.config.getProperty()

        self.assertExceptionID(u'1033', context.exception)
        self.assertEqual(
            'No such section prop_section', context.exception.message)

    def test_getProperty_root_leaf(self):
        """
        A specific property from room is returned when asked.
        """
        result = self.config.getProperty('prop_node_ro')

        self.assertEqual(u'prop_node_ro', result)

    def test_getProperty_branch(self):
        """
        A specific property from subsection is returned when asked.
        """
        result = self.config.getProperty('prop_section')

        self.assertEqual({
            'prop_ro': u'prop_ro',
            'prop_rw': u'prop_rw',
            'prop_wrapped': u'prop_wrapped',
            },
            result)

    def test_getProperty_branch_leaf(self):
        """
        A specific property from subsection is returned when asked.
        """
        result = self.config.getProperty('prop_section/prop_ro')

        self.assertEqual(u'prop_ro', result)

    def test_setProperty_non_existent(self):
        """
        An error is raise if property_path does not existes.
        """
        with self.assertRaises(NoSuchAttributeError) as context:
            self.config.setProperty('property_non_existent', 'something')

        self.assertExceptionID(u'1032', context.exception)

    def test_setProperty_read_only(self):
        """
        An error is raised when trying to write a property which is
        not writable.

        The error is `NoSuchAttributeError` since setProperty only looks
        for writable properties.
        """
        with self.assertRaises(NoSuchAttributeError):
            self.config.setProperty('prop_ro', 'something')

    def test_setProperty_section(self):
        """
        An error is raised when trying to write a property which is a
        section.

        The error is `NoSuchAttributeError` since setProperty only looks
        for writable properties and sections are not writable.
        """
        with self.assertRaises(NoSuchAttributeError):
            self.config.setProperty('prop_section', 'something')

    def test_setProperty_defined_but_non_exitent(self):
        """
        An error is raised if property is defined on the interface, but
        not existent on the object.
        """
        self.config = MissingPropertyConfigurationSection()

        with self.assertRaises(NoSuchAttributeError):
            self.config.setProperty('prop_rw', 'something')

    def test_setProperties_unknown_section(self):
        """
        An error is raised when trying to set a property for an unknown
        section.
        """
        with self.assertRaises(NoSuchSectionError) as context:
            self.config.setProperty('no_such_section/property', 'something')

        self.assertExceptionID(u'1033', context.exception)

    def test_setProperties_unknown_property(self):
        """
        An error is raised when trying to set an unknown property for a
        valid section.
        """
        with self.assertRaises(NoSuchAttributeError) as context:
            self.config.setProperty(
                'prop_section/unknown_property', 'something')

        self.assertExceptionID(u'1032', context.exception)

    def test_setProperty_ok_leaf(self):
        """
        Value is set if property exists in a leaf.
        """
        self.config.prop_section.setProperty('prop_rw', 'something')

        self.assertEqual('something', self.config.prop_section.prop_rw)

    def test_setProperty_ok_node(self):
        """
        A node containing both properties and section can still have
        a property set.
        """
        self.config.setProperty('prop_node_rw', 'something')

        self.assertEqual('something', self.config.prop_node_rw)

    def test_setProperty_ok_leaf_from_parent(self):
        """
        Value is set if property exists in a leaf of a child.
        """
        self.config.setProperty('prop_section/prop_rw', 'something')

        self.assertEqual('something', self.config.prop_section.prop_rw)

    def test_setProperty_ok_decorator(self):
        """
        Value can be set even if is defined using @property decorator.
        """
        new_value = manufacture.string()
        self.assertEqual(
            u'prop_wrapped', self.config.prop_section.prop_wrapped)
        self.config.setProperty('prop_section/prop_wrapped', new_value)

        self.assertEqual(new_value, self.config.prop_section.prop_wrapped)

    def test_createProperty_not_section(self):
        """
        Only sections can be created and requesting to create a normal
        attribute will raise NoSuchSectionError.
        """
        with self.assertRaises(NoSuchSectionError):
            self.config.createProperty('no_such_section', None)

        with self.assertRaises(NoSuchSectionError):
            self.config.createProperty('prop_section/no_such_section', None)

        with self.assertRaises(NoSuchSectionError):
            self.config.createProperty('prop_section/don-t-care', None)

    def test_createProperty_traverse(self):
        """
        createProperty will traverse the configuration tree and call
        createProperty on sub sections.
        """
        with self.Patch.object(
                self.config.prop_section, 'createProperty') as mock:
            self.config.createProperty('prop_section/some_section', None)

        mock.assert_called_once_with('some_section', None)

    def test_deleteProperty_not_section(self):
        """
        Only sections can be deleted and requesting to delete a normal
        attribute will raise NoSuchSectionError.
        """
        with self.assertRaises(NoSuchSectionError):
            self.config.deleteProperty('no_such_section')

        with self.assertRaises(NoSuchSectionError):
            self.config.deleteProperty('prop_section/no_such_section')

        with self.assertRaises(NoSuchSectionError):
            self.config.deleteProperty('prop_section/don-t-care')

    def test_deleteProperty_traverse(self):
        """
        deleteProperty will traverse the configuration tree and call
        deleteProperty on sub sections.
        """
        with self.Patch.object(
                self.config.prop_section, 'deleteProperty') as mock:
            self.config.deleteProperty('prop_section/some_section')

        mock.assert_called_once_with('some_section')
