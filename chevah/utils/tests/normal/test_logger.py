# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Test for logger.'''

from __future__ import with_statement
from logging import (
    FileHandler,
    StreamHandler,
    )
from logging.handlers import (
    RotatingFileHandler,
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


class TestLoggerFile(UtilsTestCase):
    """
    Integration tests for Logger using log files.
    """

    def _getConfiguration(self, content):

        proxy = manufacture.makeFileConfigurationProxy(
            content=content, defaults=LOG_SECTION_DEFAULTS)
        return manufacture.makeLogConfigurationSection(proxy=proxy)

    def test_configure_log_file_disabled(self):
        """
        Integration test for initializing the logger with a disabled file.
        """
        content = (
            '[log]\n'
            'log_file: Disabled\n')
        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()
        self.assertIsNone(logger._file_handler)

        logger.configure(configuration)

        self.assertIsNone(logger._file_handler)

    def _getTempFilePath(self):
        segments = manufacture.fs.temp_segments
        segments.append(manufacture.getUniqueString())
        file_path = manufacture.fs.getRealPathFromSegments(segments)
        return (file_path, segments)

    def test_configure_log_file_normal(self):
        """
        System test for using a file.
        """
        file_name, segments = self._getTempFilePath()
        content = (
            u'[log]\n'
            u'log_file: %s\n' % (file_name))
        log_id = manufacture.getUniqueInteger()
        log_message = manufacture.getUniqueString()

        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()
        try:
            logger.configure(configuration)

            # Check logger configuration.
            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(isinstance(logger._file_handler, FileHandler))

            # Add two log entries and close the logger.
            logger.log(log_id, log_message)
            logger.log(log_id + 1, log_message)
            logger.removeAllHandlers()

            # Check that file exists and it has the right content.
            self.assertTrue(manufacture.fs.exists(segments))
            log_content = manufacture.fs.getFileContent(segments)
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
        file_name, segments = self._getTempFilePath()
        content = (
            u'[log]\n'
            u'log_file: %s\n'
            u'log_file_rotate_external: Yes\n'
             ) % (file_name)

        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()

        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(
                isinstance(logger._file_handler, WatchedFileHandler))
            logger.removeAllHandlers()
        finally:
            manufacture.fs.deleteFile(segments)

    def test_configure_log_file_rotate_at_size(self):
        """
        Check file rotation at size.
        """
        file_name, segments = self._getTempFilePath()
        content = (
            u'[log]\n'
            u'log_file: %s\n'
            u'log_file_rotate_external: No\n'
            u'log_file_rotate_at_size: 100\n'
            u'log_file_rotate_count: 10\n'
             ) % (file_name)

        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()

        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(
                isinstance(logger._file_handler, RotatingFileHandler))
            self.assertEqual(10, logger._file_handler.backupCount)
            logger.removeAllHandlers()
        finally:
            manufacture.fs.deleteFile(segments)

    def test_configure_log_file_rotate_each(self):
        """
        Check file rotation archive keeping.
        """
        file_name, segments = self._getTempFilePath()
        content = (
            u'[log]\n'
            u'log_file: %s\n'
            u'log_file_rotate_external: No\n'
            u'log_file_rotate_each: 2 hours\n'
            u'log_file_rotate_count: 0\n'
             ) % (file_name)

        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()
        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(
                isinstance(logger._file_handler, TimedRotatingFileHandler))
            self.assertEqual(0, logger._file_handler.backupCount)
            self.assertEqual('H', logger._file_handler.when)
            self.assertEqual(2 * 60 * 60, logger._file_handler.interval)
            logger.removeAllHandlers()
        finally:
            manufacture.fs.deleteFile(segments)


class TestLoggerHandlers(UtilsTestCase):
    """
    Basic tests for handler(s) management.
    """
    def setUp(self):
        super(TestLoggerHandlers, self).setUp()
        log_name = manufacture.getUniqueString()
        self.logger = manufacture.makeLogger(log_name=log_name)

    def tearDown(self):
        self.logger.removeAllHandlers()
        super(TestLoggerHandlers, self).tearDown()

    def test_addHandler(self):
        """
        A LogHandler can be added to the logger and after that is called on
        all log events.
        """
        log_output = StringIO()
        log_handler = StreamHandler(log_output)
        log_entry_id = manufacture.getUniqueInteger()
        log_entry = manufacture.getUniqueString()

        self.logger.addHandler(log_handler)
        self.logger.log(log_entry_id, log_entry)

        self.assertEqual(log_entry + u'\n', log_output.getvalue())

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

    def test_removeHandlers(self):
        """
        Handler is removed and not called on further log events.
        """
        log_output = StringIO()
        log_handler = StreamHandler(log_output)
        log_entry_id = manufacture.getUniqueInteger()
        log_entry = manufacture.getUniqueString()

        self.logger.addHandler(log_handler)
        self.logger.removeHandler(log_handler)
        self.logger.log(log_entry_id, log_entry)
        handlers = self.logger.getHandlers()

        self.assertNotContains(log_handler, handlers)
        self.assertIsEmpty(handlers)
        self.assertIsEmpty(log_output.getvalue())

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

        self.logger.removeDefaultHandlers()

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


class TestLoggerWindowsEventLog(UtilsTestCase):
    """
    Integration tests for Logger using windows event logger.
    """

    def _getConfiguration(self, content):
        proxy = manufacture.makeFileConfigurationProxy(
            content=content, defaults=LOG_SECTION_DEFAULTS)
        return manufacture.makeLogConfigurationSection(proxy=proxy)

    def test_configure_disabled(self):
        """
        When windows event log is disabled it will not be added by
        logger.configure.
        """
        content = (
            '[log]\n'
            'log_windows_eventlog: Disabled\n')
        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()

        logger.configure(configuration)

        self.assertIsEmpty(logger.getHandlers())

    def test_configure_ignored_on_unix(self):
        """
        On Unix, event if windows event log is enabled it will not be added by
        logger.configure, since it is not supported on Unix.
        """
        if self.os_name != 'posix':
            raise self.skipTest()
        content = (
            '[log]\n'
            'log_windows_eventlog: something\n')
        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()

        logger.configure(configuration)

        self.assertIsEmpty(logger.getHandlers())

    def test_configure_enabled(self):
        """
        On Windows, when windows_eventlog is enabled, a handler is enabled
        using the configured source name.

        Logs are emited using the source defined by the
        log_windows_eventlog configuration option.
        """
        if self.os_name != 'nt':
            raise self.skipTest()
        from chevah.utils.logger import WindowsEventLogHandler

        content = (
            '[log]\n'
            'log_windows_eventlog: something\n')
        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()

        logger.configure(configuration)

        # A list is used to make sure a single call is made.
        windows_handlers = []
        for handler in logger.getHandlers():
            if isinstance(handler, WindowsEventLogHandler):
                windows_handlers.append(handler)

        self.assertEqual(1, len(windows_handlers))
        self.assertEqual(u'something', windows_handlers[0].appname)

    def test_emit_event_id(self):
        """
        Logger will call emit on the configured handler.
        """
        if self.os_name != 'nt':
            raise self.skipTest()

        event_id = manufacture.getUniqueInteger()
        event_text = manufacture.getUniqueString()
        content = (
            '[log]\n'
            'log_windows_eventlog: something\n')
        configuration = self._getConfiguration(content=content)
        logger = manufacture.makeLogger()
        logger.configure(configuration)
        handler = logger.getHandlers()[0]
        handler.emit = manufacture.makeMock()

        logger.log(message_id=event_id, text=event_text)

        handler.emit.assert_called_once()
