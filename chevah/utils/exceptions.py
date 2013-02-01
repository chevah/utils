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
        return 'CompatError %s - %s\n%s' % (
            str(self.event_id), self.message.encode('utf-8'), str(self.data))

    def __str__(self):
        return self.__repr__()


class UtilsException(Exception):
    """
    Generic exception used by Chevah components.

    Exceptions are used to signal various errors which can be
    handled and solved.
    """
