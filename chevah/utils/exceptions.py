# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
General exceptions for Chevah projects.
"""


class ChevahError(Exception):
    """
    Generic error used by Chevah components.

    It has an ID and data attached and is very tightly coupled with an event.

    Errors are exceptions that could not be handled.
    """

    def __init__(self, message_id=0, text=None,
                 avatar=None, peer=None, data=None):
        """
        Holds the message id and message text.
        """
        if text is None:
            text = ''

        self.id = message_id
        self.text = text
        self.avatar = avatar
        self.peer = peer
        self.data = data

    def __repr__(self):
        return '%s\n%s' % (str(self.__class__), self.__str__)

    def __str__(self):
        return '%s - %s\n%s' % (
            str(self.id), self.text.encode('utf-8'), self.data)


class ConfigurationError(ChevahError):
    '''The configuration data is not valid.

    Exception raised when something is wrong with the server
    configuration.

    This exception is raised both when the configuration file is not
    valid, it contains invalid data or the remote administration service
    is sending wrong values.

    This exception is raised only when the application has reach a state
    from which it can not continue its execution.

    In case of recoverable exceptions you should used another exception.

    It holds the message id and message text.
    '''


class OperationalException(ChevahError):
    '''The action return a generic error.'''


class ChevahException(Exception):
    """
    Generic exception used by Chevah components.

    Exceptions are used to signal various errors which can be
    handled and solved.
    """


class EventException(ChevahException):
    """
    An exception containing an event
    """

    def __init__(self, event_id, data):
        self.event_id = event_id
        self.data = data

    def __repr__(self):
        return 'EventException %s\n%s' % (
            str(self.event_id), self.data.encode('utf-8'))

    def __str__(self):
        return self.__repr__()


class TimeoutException(ChevahException):
    '''The action return a generic error.'''


class SSLException(ChevahException):
    '''Error at the SSL/TLS layer..'''
