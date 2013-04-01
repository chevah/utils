# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
General exceptions for chevah.utils project.
"""


class UtilsError(Exception):
    """
    Error raised by chevah.utils package.
    """

    def __init__(self, event_id, message, data=None):
        self.event_id = event_id
        self.message = message
        self.data = data

    def __repr__(self):
        return '%s\n%s' % (
            str(self.__class__), self.__str__())

    def __str__(self):
        return '%s - %s\n%s' % (
            str(self.event_id), self.message.encode('utf-8'), str(self.data))


class NoSuchAttributeError(UtilsError):
    """
    Error raised when the configuration does not have a requested attribute.
    """

    def __init__(self, message=''):
        self.event_id = u'1032'
        self.message = "No such property %s" % (message)
        self.data = None


class NoSuchSectionError(UtilsError):
    """
    Error raised when the configuration does not have a requested section.
    """

    def __init__(self, message=''):
        self.event_id = u'1033'
        self.message = "No such section %s" % (message)
        self.data = None


class CreateNotSupportedError(UtilsError):
    """
    Error raised when trying to create a property for which create
    is not supported.
    """

    def __init__(self, message=''):
        self.event_id = u'1034'
        self.message = "Create not supported for %s" % (message)
        self.data = None


class DeleteNotSupportedError(UtilsError):
    """
    Error raised when trying to delete a property for which delete
    is not supported.
    """

    def __init__(self, message=''):
        self.event_id = u'1035'
        self.message = "Delete not supported for %s" % (message)
        self.data = None


class UtilsException(Exception):
    """
    Generic exception used by Chevah components.

    Exceptions are used to signal various errors which can be
    handled and solved.
    """
