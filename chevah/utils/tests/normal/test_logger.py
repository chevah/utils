# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Test for logger.'''

from __future__ import with_statement
from logging import (
    FileHandler,
    NullHandler,
    StreamHandler,
    )
from logging.handlers import (
    RotatingFileHandler,
    SysLogHandler,
    TimedRotatingFileHandler,
    )
from StringIO import StringIO
from time import time
import random

from chevah.utils.constants import LOG_SECTION_DEFAULTS
from chevah.utils.logger import (
    LogEntry,
    StdOutHandler,
    WatchedFileHandler,
    WindowsEventLogHandler,
    )
from chevah.utils.testing import manufacture, UtilsTestCase


class InMemoryHandler(NullHandler, object):
    """
    Handlers that stores logged record in memory.
    """

    def __init__(self):
        super(InMemoryHandler, self).__init__()
        self.history = []
        self.name = 'in-memory'

    def emit(self, record):
        self.history.append(record)

    def handle(self, record):
        self.emit(record)


class LoggerTestCase(UtilsTestCase):
    """
    TestCase for the logger.
    """

    def getConfiguration(self, content=None):
        """
        Return logger configuration object.
        """
        if content is None:
            content = (
                '[log]\n'
                'log_file: Disabled\n'
                )

        proxy = manufacture.makeFileConfigurationProxy(
            content=content, defaults=LOG_SECTION_DEFAULTS)
        return manufacture.makeLogConfigurationSection(proxy=proxy)


class TestLogEntry(UtilsTestCase):
    '''LogEntry tests.'''

    def test_init(self):
        """
        Check LogEntry initialization.
        """
        log_id = 999999
        log_text = manufacture.getUniqueString()
        log_avatar = manufacture.makeFilesystemApplicationAvatar()
        log_peer = manufacture.makeIPv4Address()
        entry = LogEntry(log_id, log_text, log_avatar, log_peer)
        now = time()
        self.assertEqual(log_id, entry.message_id)
        self.assertEqual(log_text, entry.text)
        self.assertEqual(log_avatar, entry.avatar)
        self.assertEqual(log_peer, entry.peer)

        # We just check that human representation of time not empty.
        self.assertTrue(entry.timestamp_hr)

        # We just test that the entry's timestamp is very recent.
        time_diff = now - entry.timestamp
        self.assertTrue(time_diff <= 0.05, 'Timediff is %f' % time_diff)
        self.assertTrue(time_diff >= 0.0, 'Timediff is %f' % time_diff)

    def test_avatar_hr_no_data(self):
        """
        Check human readable format for an avatar with no data.
        """
        entry = LogEntry(None, None, None, None)
        self.assertEqual(u'None', entry.avatar_hr)

    def test_peer_hr_no_data(self):
        """
        Check human readable format for an peer with no data.
        """
        entry = LogEntry(None, None, None, None)
        self.assertEqual(u'None', entry.peer_hr)

    def test_avatar_hr_with_data(self):
        """
        Check human readable format for an avatar with data.
        """
        log_avatar = manufacture.makeFilesystemApplicationAvatar()
        entry = LogEntry(None, None, log_avatar, None)
        self.assertEqual(log_avatar.name, entry.avatar_hr)

    def test_peer_hr_with_data(self):
        """
        Check human readable format for a peer with data.
        """
        peer = manufacture.makeIPv4Address()
        entry = LogEntry(None, None, None, peer)
        expected_peer_string = (u'%s:%d' % (peer.host, peer.port))
        self.assertEqual(expected_peer_string, entry.peer_hr)


class TestLogger(LoggerTestCase):
    """
    Basic tests for log handlers management.
    """
    def setUp(self):
        super(TestLogger, self).setUp()
        log_name = manufacture.getUniqueString()
        self.config = self.getConfiguration()
        self.logger = manufacture.makeLogger(log_name=log_name)

    def tearDown(self):
        self.logger.removeAllHandlers()
        super(TestLogger, self).tearDown()

    def test_configure_all(self):
        """
        It will add all handlers as store them in `_active_handlers`.
        """
        self.config.file = manufacture.string()
        self.config.syslog = manufacture.string()
        self.config.windows_eventlog = manufacture.string()
        file_handler = object()
        syslog_handler = object()
        windows_eventlog_handler = object()
        self.logger._addFile = self.Mock(return_value=file_handler)
        self.logger._addSyslog = self.Mock(return_value=syslog_handler)
        self.logger._addWindowsEventLog = self.Mock(
            return_value=windows_eventlog_handler)

        self.logger.configure(configuration=self.config)

        self.logger._addFile.assert_called_once_with()
        self.assertEqual(
            self.logger._active_handlers['file'], file_handler)
        self.assertEqual(
            self.logger._active_handlers['syslog'], syslog_handler)

        if self.os_name == 'nt':
            self.assertEqual(
                self.logger._active_handlers['windows_eventlog'],
                windows_eventlog_handler,
                )

    def test_configure_multiple_times(self):
        """
        An error is raised when trying to configure the logger more
        than once.
        """
        self.logger.configure(configuration=self.config)

        with self.assertRaises(AssertionError):
            self.logger.configure(configuration=self.config)

    def test_configure_subscribers(self):
        """
        Configure will subscribe to changes on the configuration.
        """
        self.logger.configure(configuration=self.config)
        self.logger._reconfigureHandler = self.Mock()

        self.config.file = manufacture.string()
        self.logger._reconfigureHandler.assert_called_once_with(
            name=u'file', setter=self.logger._addFile)

        self.logger._reconfigureHandler = self.Mock()
        self.config.syslog = manufacture.string()
        self.logger._reconfigureHandler.assert_called_once_with(
            name=u'syslog', setter=self.logger._addSyslog)

        self.logger._reconfigureHandler = self.Mock()
        self.config.windows_eventlog = manufacture.string()
        self.logger._reconfigureHandler.assert_called_once_with(
            name=u'windows_eventlog', setter=self.logger._addWindowsEventLog)

    def test_reconfigureHandler_new(self):
        """
        It will set the new handler and remove the old one.
        """
        old_handler = InMemoryHandler()
        new_handler = InMemoryHandler()
        old_handler.close = self.Mock()
        self.logger.addHandler(old_handler)
        self.logger._active_handlers['file'] = old_handler

        def setter():
            self.logger.addHandler(new_handler)
            return new_handler

        self.logger._reconfigureHandler(name='file', setter=setter)

        self.assertEqual(new_handler, self.logger._active_handlers['file'])
        old_handler.close.assert_called_once_with()
        handlers = self.logger.getHandlers()
        self.assertEqual(1, len(handlers))
        self.assertEqual(new_handler, handlers[0])

    def test_reconfigureHandler_failure(self):
        """
        On failure, It will keep the existing handler and propagate the error.
        """
        old_handler = InMemoryHandler()
        old_handler.close = self.Mock()
        self.logger.addHandler(old_handler)
        self.logger._active_handlers['file'] = old_handler

        def setter():
            raise AssertionError('fail-mark')

        with self.assertRaises(AssertionError) as context:
            self.logger._reconfigureHandler(name='file', setter=setter)

        self.assertEqual('fail-mark', context.exception.message)
        self.assertEqual(old_handler, self.logger._active_handlers['file'])
        self.assertFalse(old_handler.close.called)

    def test_addSyslog_disabled(self):
        """
        It does nothing when syslog is not enabled.
        """
        self.config.syslog = None
        self.logger._configuration = self.config

        result = self.logger._addSyslog()

        self.assertIsNone(result)

    def test_addSyslog_enabled(self):
        """
        When syslog is enabled it will be added and returned.
        """
        # We just set a local TCP port, since it will initialize without
        # errors.
        self.config.syslog = '127.0.0.1:10000'
        self.logger._configuration = self.config

        result = self.logger._addSyslog()

        self.assertIsInstance(result, SysLogHandler)
        handlers = self.logger.getHandlers()
        self.assertEqual(1, len(handlers))
        self.assertEqual(result, handlers[0])

    def test_addWindowsEventLog_disabled(self):
        """
        It does nothing when windows_eventlog is not enabled.
        """
        self.config.windows_eventlog = None
        self.logger._configuration = self.config

        result = self.logger._addWindowsEventLog()

        self.assertIsNone(result)

    def test_addWindowsEventLog_enabled(self):
        """
        When windows_eventlog is enabled it will be added and returned.
        """
        self.config.windows_eventlog = manufacture.ascii()
        self.logger._configuration = self.config

        result = self.logger._addWindowsEventLog()

        if self.os_name != 'nt':
            self.assertIsNone(result)
        else:
            self.assertIsInstance(WindowsEventLogHandler, result)
            self.assertEqual(
                self.config.windows_eventlog, result.appname)
            handlers = self.logger.getHandlers()
            self.assertEqual(1, len(handlers))
            self.assertEqual(result, handlers[0])

    def test_addFile_disabled(self):
        """
        It does nothing if log file is not enabled.
        """
        self.config.file = None
        self.logger._configuration = self.config

        result = self.logger._addFile()

        self.assertIsNone(result)

    def test_configure_log_file_normal(self):
        """
        System test for using a file.
        """
        file_name, segments = manufacture.fs.makePathInTemp()
        content = (
            u'[log]\n'
            u'log_file: %s\n' % (file_name))
        log_id = manufacture.getUniqueInteger()
        log_message = manufacture.getUniqueString()

        configuration = self.getConfiguration(content=content)
        logger = manufacture.makeLogger()
        try:
            logger.configure(configuration)

            # Check logger configuration.
            self.assertIsNotNone(logger._active_handlers['file'])
            self.assertIsInstance(
                FileHandler, logger._active_handlers['file'])

            # Add two log entries and close the logger.
            logger.log(log_id, log_message)
            logger.log(log_id + 1, log_message)
            logger.removeAllHandlers()

            # Check that file exists and it has the right content.
            self.assertTrue(manufacture.fs.exists(segments))
            log_content = manufacture.fs.getFileLines(segments)
            self.assertEqual(2, len(log_content))
            self.assertStartsWith(str(log_id), log_content[0])
            self.assertEndsWith(log_message, log_content[0])
            self.assertStartsWith(str(log_id + 1), log_content[1])
        finally:
            manufacture.fs.deleteFile(segments)

    def test_configure_log_file_rotate_external(self):
        """
        Check file rotation.
        """
        file_name, segments = manufacture.fs.makePathInTemp()
        content = (
            u'[log]\n'
            u'log_file: %s\n'
            u'log_file_rotate_external: Yes\n'
             ) % (file_name)

        configuration = self.getConfiguration(content=content)
        logger = manufacture.makeLogger()

        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._active_handlers['file'])
            self.assertIsInstance(
                WatchedFileHandler, logger._active_handlers['file'])
            logger.removeAllHandlers()
        finally:
            manufacture.fs.deleteFile(segments)

    def test_configure_log_file_rotate_at_size(self):
        """
        Check file rotation at size.
        """
        file_name, segments = manufacture.fs.makePathInTemp()
        content = (
            u'[log]\n'
            u'log_file: %s\n'
            u'log_file_rotate_external: No\n'
            u'log_file_rotate_at_size: 100\n'
            u'log_file_rotate_count: 10\n'
             ) % (file_name)

        configuration = self.getConfiguration(content=content)
        logger = manufacture.makeLogger()

        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._active_handlers['file'])
            self.assertIsInstance(
                RotatingFileHandler, logger._active_handlers['file'])
            self.assertEqual(10, logger._active_handlers['file'].backupCount)
            logger.removeAllHandlers()
        finally:
            manufacture.fs.deleteFile(segments)

    def test_configure_log_file_rotate_each(self):
        """
        Check file rotation archive keeping.
        """
        file_name, segments = manufacture.fs.makePathInTemp()
        content = (
            u'[log]\n'
            u'log_file: %s\n'
            u'log_file_rotate_external: No\n'
            u'log_file_rotate_each: 2 hours\n'
            u'log_file_rotate_count: 0\n'
             ) % (file_name)

        configuration = self.getConfiguration(content=content)
        logger = manufacture.makeLogger()
        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._active_handlers['file'])
            self.assertIsInstance(
                TimedRotatingFileHandler, logger._active_handlers['file'])
            self.assertEqual(0, logger._active_handlers['file'].backupCount)
            self.assertEqual(u'H', logger._active_handlers['file'].when)
            self.assertEqual(
                2 * 60 * 60, logger._active_handlers['file'].interval)
            logger.removeAllHandlers()
        finally:
            manufacture.fs.deleteFile(segments)

    def test_addFile_file_rotate_each_zero(self):
        """
        It is not enabled when interval is zero (or less than zero).
        """
        path, self.test_segments = manufacture.fs.makePathInTemp()
        self.config.file = path
        self.config.file_rotate_each = (0, 'd')
        self.logger._configuration = self.config

        result = self.logger._addFile()

        self.assertIsInstance(FileHandler, result)

    def test_addHandler_with_name(self):
        """
        It adds the handler and sends a notification.

        After that the handler is called on all log events.
        """
        log_handler = InMemoryHandler()
        log_entry_id = manufacture.getUniqueInteger()
        log_entry = manufacture.getUniqueString()
        callback = self.Mock()
        self.logger.subscribe('add-handler', callback)

        self.logger.addHandler(log_handler)
        self.logger.log(log_entry_id, log_entry)

        self.assertEqual(log_entry, log_handler.history[0].text)
        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(log_handler._name, signal.name)

    def test_addHandler_without_name(self):
        """
        It adds the handler and does not sends a notification.
        """
        log_handler = InMemoryHandler()
        log_handler.name = None
        callback = self.Mock()
        self.logger.subscribe('add-handler', callback)

        self.logger.addHandler(log_handler)

        self.assertFalse(callback.called)

    def test_getHandlers_initially_empty(self):
        """
        Logger contains no handlers when created.
        """
        handlers = self.logger.getHandlers()

        self.assertIsEmpty(handlers)

    def test_getHandlers(self):
        """
        Logger exports list with active handler(s).
        """
        log_output = StringIO()
        log_handler = StreamHandler(log_output)

        self.logger.addHandler(log_handler)
        handlers = self.logger.getHandlers()

        self.assertEqual(len(handlers), 1)
        self.assertContains(log_handler, handlers)

    def test_removeHandler_success(self):
        """
        It removes and closes the handler, sending a notification.

        Handler is not called on further log events.
        """
        log_handler = InMemoryHandler()
        log_entry_id = manufacture.getUniqueInteger()
        log_entry = manufacture.getUniqueString()
        self.logger.addHandler(log_handler)
        callback = self.Mock()
        self.logger.subscribe('remove-handler', callback)
        self.assertIsNotEmpty(self.logger.getHandlers())

        self.logger.removeHandler(log_handler)

        # No entry is recorded by the handler.
        self.logger.log(log_entry_id, log_entry)
        self.assertIsEmpty(log_handler.history)

        # No handlers are there.
        self.assertIsEmpty(self.logger.getHandlers())

        self.assertEqual(1, callback.call_count)
        signal = callback.call_args[0][0]
        self.assertEqual(log_handler._name, signal.name)

    def test_removeHandler_none(self):
        """
        When `None` is requested to be removed, nothing happens.
        """
        callback = self.Mock()
        self.logger.subscribe('remove-handler', callback)

        self.logger.removeHandler(None)

        self.assertFalse(callback.called)

    def test_removeHandler_without_name(self):
        """
        When handler has no name, it is just removed without sending
        a notification.
        """
        log_handler = InMemoryHandler()
        log_handler.name = None
        self.logger.addHandler(log_handler)
        callback = self.Mock()
        self.logger.subscribe('remove-handler', callback)

        self.logger.removeHandler(log_handler)

        self.assertFalse(callback.called)

    def test_removeHandler_closes_handler(self):
        """
        Handlers are closed when they are removed from the logger.
        """
        log_output = StringIO()

        class DummyStreamHandlerWithClose(StreamHandler):
            def close(self):
                self.stream.close()
                StreamHandler.close(self)

        log_handler = DummyStreamHandlerWithClose(log_output)
        self.logger.addHandler(log_handler)
        self.logger.removeHandler(log_handler)

        self.assertTrue(log_output.closed)

    def test_removeAllHandlers(self):
        """
        All handlers are removed.
        """
        log_output = StringIO()
        log_handler1 = StreamHandler(log_output)
        log_handler2 = StreamHandler(log_output)
        self.logger.addHandler(log_handler1)
        self.logger.addHandler(log_handler2)

        self.logger.removeAllHandlers()

        self.assertIsEmpty(self.logger.getHandlers())

    def test_addDefaultStdOutHandler(self):
        """
        addDefaultStdOutHandler will add a StdOutHandler.
        """
        self.logger.addDefaultStdOutHandler()

        handlers = self.logger.getHandlers()

        self.assertEqual(1, len(handlers))
        self.assertIsInstance(StdOutHandler, handlers[0])
        self.assertEqual(
            handlers[0], self.logger._log_stdout_handler)

    def test_addDefaultWindowsEventLogHandlers(self):
        """
        addDefaultWindowsEventLogHandler will add a WindowsEventLogHandler.
        """
        if self.os_name != 'nt':
            raise self.skipTest()

        self.logger.addDefaultWindowsEventLogHandler('some-name')

        handlers = self.logger.getHandlers()

        self.assertEqual(1, len(handlers))
        self.assertIsInstance(WindowsEventLogHandler, handlers[0])
        self.assertEqual(
            handlers[0], self.logger._log_ntevent_handler)

    def test_removeDefaultHandlers(self):
        """
        removeDefaultHandlers will remove all configured default handlers.
        """
        self.logger.addDefaultStdOutHandler()
        if self.os_name == 'nt':
            self.logger.addDefaultWindowsEventLogHandler('some-name')

        self.logger._removeDefaultHandlers()

        handlers = self.logger.getHandlers()
        self.assertIsEmpty(handlers)


class TestWindowsEventLogHandler(UtilsTestCase):
    """
    Tests for WindowsEventLogHandler.
    """

    @classmethod
    def setUpClass(cls):
        """
        These are windows specific tests, so skip all.
        """
        if cls.os_name != 'nt':
            raise cls.skipTest()

    def test_init(self):
        """
        Check hanlder initialization.
        """
        source_name = manufacture.getUniqueString()
        handler = WindowsEventLogHandler(source_name)

        self.assertEqual(source_name, handler.appname)

    def test_getMessageID_no_integer(self):
        """
        1 is returned if log_entry/record does not have a valid integer ID.
        """
        source_name = manufacture.getUniqueString()
        handler = WindowsEventLogHandler(source_name)
        record = LogEntry('no_int', 'don-t care')

        result = handler.getMessageID(record)

        self.assertEqual(1, result)

    def test_getMessageID_no_id(self):
        """
        1 is returned if log_entry/record does not have an id.
        """
        source_name = manufacture.getUniqueString()
        handler = WindowsEventLogHandler(source_name)
        record = self.Bunch()

        result = handler.getMessageID(record)

        self.assertEqual(1, result)

    def test_getMessageID_valid(self):
        """
        The event id is returned if log_entry/record has a valid id.
        """
        source_name = manufacture.getUniqueString()
        handler = WindowsEventLogHandler(source_name)
        record = self.Bunch(message_id='2')

        result = handler.getMessageID(record)

        self.assertEqual(2, result)

        # Let's try with an int.
        record = self.Bunch(message_id=3)
        result = handler.getMessageID(record)
        self.assertEqual(3, result)

    def test_emit_system(self):
        """
        This is a system test to check that handler.emit() reached
        windows event log.
        """
        # Source name is static to know where to look at.
        # We will use event_id and content to identity an emited log.
        source_name = 'chevah-server-test-suite'
        # Unique string/number are only unique inside a single test run.
        # Since we interact with external system we need to generate
        # some more random values.
        event_id = random.randint(0, 50000)
        text = unicode(manufacture.uuid4())

        handler = WindowsEventLogHandler(source_name)
        record = LogEntry(event_id, text)

        handler.emit(record)

        event = self.getWindowsEvent(
            source_name=source_name, event_id=event_id)

        # We got an event from our static source with a random ID.
        # Now check that content is right.
        self.assertEqual(1, len(event.StringInserts))
        self.assertEqual(text, event.StringInserts[0])

    def getWindowsEvent(self, source_name, event_id):
        """
        Search Windows Event logger for localhost and return event for
        source_name with event_id.
        """
        import win32evtlog
        hand = win32evtlog.OpenEventLog(None, 'Application')
        flags = (
            win32evtlog.EVENTLOG_BACKWARDS_READ |  # New events firsts.
            win32evtlog.EVENTLOG_SEQUENTIAL_READ
            )
        try:
            events = True
            while events:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
                for event in events:
                    if (event.EventID == event_id and
                            event.SourceName == source_name):
                        return event
        finally:
            win32evtlog.CloseEventLog(hand)

        return None
