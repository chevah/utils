# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
"""
Observer implementation for Chevah project.
"""


class Signal(object):
    """
    An signal trigerred by the observer.

    It contains a source together with aditional arguments privided by the
    triggering call.
    """

    def __init__(self, source, **kwargs):
        self.source = source
        for key, value in kwargs.iteritems():
            setattr(self, key, value)


class HasObserver(object):
    """
    A base class for implementing observers.

    The internal subscribers database is kept by `_subscribers`.
    Since this class is designed to be used as an mixin the `_subscribers`
    member is generated on-demand.
    """

    def unsubscribe(self, name=None, callback=None):
        """
        Unsubscribe callbacks.

        If `callback` is None, all callbacks for `name` will be removed.
        If `name` is None all callbacks will be removed.
        """
        if not hasattr(self, '_subscribers'):
            '''No subscribers defined yet.'''
            return
        if name is None:
            self._subscribers = {}
        else:
            if callback is None:
                self._subscribers[name] = []
            else:
                self._subscribers[name].remove(callback)

    def subscribe(self, name, callback):
        """
        Subscribe the callback to signal with `name`.
        """
        subscribers = getattr(self, '_subscribers', {})
        self._subscribers = subscribers
        if name in self._subscribers:
            '''Append the callback to the existing list.'''
            if not callback in self._subscribers[name]:
                '''Avoid adding the same callback multiple times.'''
                self._subscribers[name].append(callback)
        else:
            '''Create a new list with the initial callback.'''
            self._subscribers[name] = [callback]

    def notify(self, name, signal=None):
        """
        Trigger all subscribers with name.
        """
        if not hasattr(self, '_subscribers'):
            '''No subscribers defined yet.'''
            return

        if name in self._subscribers:
            '''Only call if we have subscribers for `name`.'''
            for callback in self._subscribers[name]:
                callback(signal)
