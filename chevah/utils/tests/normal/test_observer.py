# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Unit tests for observer module.'''
from __future__ import with_statement

from chevah.empirical.testcase import TestCase
from chevah.utils.observer import ObserverMixin, Signal


class TestSignal(TestCase):
    '''Signal tests.'''

    def test_signal_init(self):
        """
        Check Signal initialization.
        """
        with self.assertRaises(TypeError):
            Signal()
        signal = Signal(source=self)
        self.assertEqual(signal.source, self)

        signal = Signal(source=self, key=u'value')
        self.assertEqual(signal.key, u'value')


class TestObserverMixin(TestCase):
    '''FileConfiguration.'''

    def test_init(self):
        """
        Check ObserverMixin initialization.
        """
        observer = ObserverMixin()
        self.assertFalse(hasattr(observer, '_subscribers'))

    def test_subscribe(self):
        """
        Check subscribe.
        """
        observer = ObserverMixin()

        def one_callback(signal):
            pass

        def another_callback(signal):
            pass

        observer.subscribe('signal', one_callback)
        self.assertEqual(1, len(observer._subscribers))
        self.assertEqual(1, len(observer._subscribers['signal']))
        self.assertTrue(one_callback in observer._subscribers['signal'])

        # Adding the same callback more than once will only add it once.
        observer.subscribe('signal', another_callback)
        observer.subscribe('signal', another_callback)
        self.assertEqual(1, len(observer._subscribers))
        self.assertEqual(2, len(observer._subscribers['signal']))
        self.assertTrue(another_callback in observer._subscribers['signal'])

        observer.subscribe('another_signal', another_callback)
        self.assertEqual(2, len(observer._subscribers))
        self.assertEqual(1, len(observer._subscribers['another_signal']))
        self.assertTrue(
            another_callback in observer._subscribers['another_signal'])

    def test_notify(self):
        """
        Check notify.
        """
        observer = ObserverMixin()
        self.signals_called = []

        def one_callback(signal):
            self.signals_called.append({
                'source': u'one_callback',
                'signal': signal,
                })

        def another_callback(signal):
            self.signals_called.append({
                'source': u'another_callback',
                'signal': signal,
                })

        signal = Signal(source=self)
        observer.subscribe('signal-name', one_callback)
        observer.notify('signal-name', signal)
        self.assertEqual(1, len(self.signals_called))
        self.assertEqual(u'one_callback', self.signals_called[0]['source'])
        self.assertEqual(signal, self.signals_called[0]['signal'])

        self.signals_called = []
        observer.subscribe('signal-name', another_callback)
        observer.notify('signal-name', signal)
        self.assertEqual(2, len(self.signals_called))
        self.assertEqual(u'one_callback', self.signals_called[0]['source'])
        self.assertEqual(signal, self.signals_called[0]['signal'])
        self.assertEqual(
            u'another_callback', self.signals_called[1]['source'])
        self.assertEqual(signal, self.signals_called[1]['signal'])

    def test_unsubscribe_all(self):
        """
        Check unsubscribe.
        """
        observer = ObserverMixin()

        def one_callback(signal):
            pass

        def another_callback(signal):
            pass

        observer.subscribe('signal1', one_callback)
        observer.subscribe('signal2', one_callback)
        self.assertEqual(2, len(observer._subscribers))
        observer.unsubscribe()
        self.assertEqual(0, len(observer._subscribers))

    def test_unsubscribe_all_signal(self):
        """
        Check unsubscribe for a specific signal.
        """
        observer = ObserverMixin()

        def one_callback(signal):
            pass

        def another_callback(signal):
            pass

        observer.subscribe('signal1', one_callback)
        observer.subscribe('signal1', another_callback)
        observer.subscribe('signal2', one_callback)
        self.assertEqual(2, len(observer._subscribers))
        observer.unsubscribe(name='signal1')
        self.assertEqual(2, len(observer._subscribers))
        self.assertEqual(0, len(observer._subscribers['signal1']))
        self.assertEqual(1, len(observer._subscribers['signal2']))

    def test_unsubscribe_callback(self):
        """
        Check unsubscribe for a specific callback.
        """
        observer = ObserverMixin()

        def one_callback(signal):
            pass

        def another_callback(signal):
            pass

        observer.subscribe('signal1', one_callback)
        observer.subscribe('signal1', another_callback)
        observer.subscribe('signal2', one_callback)
        self.assertEqual(2, len(observer._subscribers))
        observer.unsubscribe(name='signal1', callback=another_callback)
        self.assertEqual(2, len(observer._subscribers))
        self.assertEqual(1, len(observer._subscribers['signal1']))
        self.assertTrue(one_callback in observer._subscribers['signal1'])
        self.assertFalse(another_callback in observer._subscribers['signal1'])
        self.assertEqual(1, len(observer._subscribers['signal2']))
