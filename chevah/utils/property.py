# Copyright (c) 2011-2013 Adi Roiban.
# See LICENSE for details.
"""
P
"""
from zope.interface import implements

from chevah.utils.exceptions import (
    CreateNotSupportedError,
    DeleteNotSupportedError,
    NoSuchAttributeError,
    NoSuchSectionError,
    )
from chevah.utils.interfaces import (
    IPropertyMixin,
    PublicAttribute,
    PublicSectionAttribute,
    PublicWritableAttribute
    )


class PropertyMixin(object):
    """
    Mixin for object exporting public properties.

    See `IPropertyMixin`.
    """

    implements(IPropertyMixin)

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

    @property
    def parent(self):
        """
        See: `IPropertyMixin`.
        """
        return self._parent

    def getPublicAttributeNames(self):
        """
        Return the list of all names of public attributes.
        """
        return self._getAttributeNames(PublicAttribute)

    def getPublicWritableAttributeNames(self):
        """
        Return the list of all names of public attributes.
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
        try:
            setattr(self, name, value)
        except AttributeError:
            raise NoSuchAttributeError(name)

    def getSection(self, name):
        """
        Return the branch with `name`.

        Raise MissingSectionError if branch does not exists.
        """
        try:
            return getattr(self, name)
        except AttributeError:
            raise NoSuchSectionError(name)

    def traversePath(self, property_path):
        """
        Parse property_path and return head and tail.
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

        if head == '':
            head = None

        if tail == '':
            tail = None

        return (head, tail)

    def getProperty(self, property_path=None):
        """
        See `IPropertyMixin`.
        """
        head, tail = self.traversePath(property_path)

        result = {}

        # Look for direct attributes.
        for name in self.getPublicAttributeNames():
            value = self.getAttribute(name)

            # Return direct property.
            if head and head == name:
                return value

            result.update({name: value})

        # Then for sections.
        for name in self.getPublicSectionNames():
            value = self.getSection(name)
            section_properties = value.getProperty(tail)

            # Return direct subsections.
            if head and head == name:
                return section_properties

            result.update({name: section_properties})

        return result

    def setProperty(self, property_path, value):
        """
        See `IPropertyMixin`.
        """
        head, tail = self.traversePath(property_path)

        if tail is None:
            for name in self.getPublicWritableAttributeNames():
                if name != head:
                    continue

                self.setAttribute(head, value)
                return

            # If we are here, it means that property was not found or it is
            # not writeable.
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
        See `IPropertyMixin`.
        """
        if property_path is None:
            raise DeleteNotSupportedError()

        head, tail = self.traversePath(property_path)

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
        See `IPropertyMixin`.
        """
        if property_path is None:
            raise CreateNotSupportedError()

        head, tail = self.traversePath(property_path)

        # Right now only sections support add operations.
        for name in self.getPublicSectionNames():
            if name != head:
                continue

            section = self.getSection(name)
            return section.createProperty(tail, value)

        # If we are here, it means that section was not found.
        raise NoSuchSectionError(head)
