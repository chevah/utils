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


class NoSuchPropertyError(UtilsError):
    """
    Error raised when the configuration does not have a requested property.
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


class MissingPropertyError(UtilsError):
    """
    Error raised when the configuration object does not implements a property.
    """

    def __init__(self, message=''):
        self.event_id = u'1034'
        self.message = "Property not implemented %s" % (message)
        self.data = None


class MissingSectionError(UtilsError):
    """
    Error raised when the configuration object does not implements a section.
    """

    def __init__(self, message=''):
        self.event_id = u'1035'
        self.message = "Section not implemented %s" % (message)
        self.data = None


class UtilsException(Exception):
    """
    Generic exception used by Chevah components.

    Exceptions are used to signal various errors which can be
    handled and solved.
    """
