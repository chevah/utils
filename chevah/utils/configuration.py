# Copyright (c) 2011-2013 Adi Roiban.
# See LICENSE for details.
"""
The goal of this module is to provide a storage independent configuration
tree.

Property is any member of the configuration.
It can be:
* attribute - direct property
* section - property which has other properties
"""
from chevah.utils import __python_future__

from zope.interface import implements

from chevah.utils.exceptions import (
    CreateNotSupportedError,
    DeleteNotSupportedError,
    NoSuchAttributeError,
    NoSuchSectionError,
    )
from chevah.utils.interfaces import (
    IConfigurationSection,
    PublicAttribute,
    PublicSectionAttribute,
    PublicWritableAttribute
    )
from chevah.utils.observer import Signal, ObserverMixin


class WithConfigurationPropertyMixin(object):
    """
    See `_IWithPropertiesMixin`.

    Mixin for object exporting configuration properties.
    """

    def _getAttributeNames(self, kind):
        """
        Iterate over all interfaces and return the name of the attributes
        that are instances of `kind`.
        """
        for interface in self.__implemented__.flattened():
            for name, description in interface.namesAndDescriptions():
                if not isinstance(description, kind):
                    continue
                yield name

    def getPulicAttributeNames(self):
        """
        Retrun the list of all names of public attributes.
        """
        return self._getAttributeNames(PublicAttribute)

    def getPulicWritableAttributeNames(self):
        """
        Retrun the list of all names of public attributes.
        """
        return self._getAttributeNames(PublicWritableAttribute)

    def getPublicSectionNames(self):
        """
        Return the list of all names for public sections.
        """
        return self._getAttributeNames(PublicSectionAttribute)

    def getAttribute(self, name):
        """
        Return the value of attribute with `name`.

        Raise MissingAttributeError if leaf does not exists.
        """
        try:
            return getattr(self, name)
        except AttributeError:
            raise NoSuchAttributeError(name)

    def setAttribute(self, name, value):
        """
        Set value for attribute with name.
        """
        if not hasattr(self, name):
            raise NoSuchAttributeError(name)

        setattr(self, name, value)

    def getSection(self, name):
        """
        Return the branch with `name`.

        Raise MissingSectionError if branch does not exists.
        """
        try:
            return getattr(self, name)
        except AttributeError:
            raise NoSuchSectionError(name)

    def getProperty(self, property_path=None):
        """
        See `_IWithPropertiesMixin`.
        """
        if property_path:
            try:
                head, tail = property_path.split('/', 1)
            except ValueError:
                head = property_path
                tail = None
        else:
            head = None
            tail = None

        result = {}

        # Look for direct attributes.
        for name in self.getPulicAttributeNames():
            value = self.getAttribute(name)

            # Return direct property.
            if head and head == name:
                return value

            result.update({name: value})

        # Then for sections.
        for name in self.getPublicSectionNames():
            value = self.getSection(name)
            section_properties = value.getProperty(tail)

            # Retrun direct subsections.
            if head and head == name:
                return section_properties

            result.update({name: section_properties})

        return result

    def setProperty(self, property_path, value):
        """
        See `_IWithPropertiesMixin`.
        """
        try:
            head, tail = property_path.split('/', 1)
        except ValueError:
            head = property_path
            tail = None

        if tail is None:
            for name in self.getPulicWritableAttributeNames():
                if name != head:
                    continue

                self.setAttribute(head, value)
                return

            # If we are here, it means that property was not found or it is
            # not writable.
            raise NoSuchAttributeError(head)
        else:
            for name in self.getPublicSectionNames():
                if name != head:
                    continue

                section = self.getSection(name)
                section.setProperty(tail, value)
                # We stop the search here.
                return

            # If we are here, it means that section was not found.
            raise NoSuchSectionError(head)

    def deleteProperty(self, property_path):
        """
        See `_IWithPropertiesMixin`.
        """
        if property_path is None:
            raise DeleteNotSupportedError()

        try:
            head, tail = property_path.split('/', 1)
        except ValueError:
            head = property_path
            tail = None

        # Right now only sections support delete operation.
        for name in self.getPublicSectionNames():
            if name != head:
                continue

            section = self.getSection(name)
            return section.deleteProperty(tail)

        # If we are here, it means that section was not found.
        raise NoSuchSectionError(head)

    def createProperty(self, property_path, value):
        """
        See `_IWithPropertiesMixin`.
        """
        if property_path is None:
            raise CreateNotSupportedError()

        try:
            head, tail = property_path.split('/', 1)
        except ValueError:
            head = property_path
            tail = None

        # Right now only sections support add operations.
        for name in self.getPublicSectionNames():
            if name != head:
                continue

            section = self.getSection(name)
            return section.createProperty(tail, value)

        # If we are here, it means that section was not found.
        raise NoSuchSectionError(head)


class ConfigurationSectionMixin(
        ObserverMixin, WithConfigurationPropertyMixin):
    """
    Mixin for a configuration section.
    """

    implements(IConfigurationSection)

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
