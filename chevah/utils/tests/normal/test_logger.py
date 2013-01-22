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

from chevah.empirical import ChevahTestCase, factory
from chevah.utils.logger import (
    LogEntry,
    WatchedFileHandler,
    )


class TestLogEntry(ChevahTestCase):
    '''LogEntry tests.'''

    def test_init(self):
        """
        Check LogEntry initialization.
        """
        log_id = 999999
        log_text = factory.getUniqueString()
        log_avatar = factory.makeApplicationAvatar()
        log_peer = factory.makeIPv4Address()
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
        log_avatar = factory.makeApplicationAvatar()
        entry = LogEntry(None, None, log_avatar, None)
        self.assertEqual(log_avatar.name, entry.avatar_hr)

    def test_peer_hr_with_data(self):
        """
        Check human readable format for a peer with data.
        """
        peer = factory.makeIPv4Address()
        entry = LogEntry(None, None, None, peer)
        expected_peer_string = (u'%s:%d' % (peer.host, peer.port))
        self.assertEqual(expected_peer_string, entry.peer_hr)


class TestLoggerFile(ChevahTestCase):
    """
    Integration tests for Logger using log files.
    """

    def _getConfiguration(self, content):
        defaults = {
            'log_file': 'Disabled',
            'log_file_rotate_external': 'No',
            'log_file_rotate_at_size': 'Disabled',
            'log_file_rotate_each': 'Disabled',
            'log_file_rotate_count': 'Disabled',
            'log_syslog': 'Disabled',
            }
        proxy = factory.makeFileConfigurationProxy(
            content=content, defaults=defaults)
        return factory.makeLogConfigurationSection(proxy=proxy)

    def test_configure_log_file_disabled(self):
        """
        Integration test for initializing the logger with a disabled file.
        """
        content = (
            '[log]\n'
            'log_file: Disabled\n')
        configuration = self._getConfiguration(content=content)
        logger = factory.makeLogger()
        self.assertIsNone(logger._file_handler)

        logger.configure(configuration)

        self.assertIsNone(logger._file_handler)

    def _getTempFilePath(self):
        segments = factory.fs.temp_segments
        segments.append(factory.getUniqueString())
        file_path = factory.fs.getRealPathFromSegments(segments)
        return (file_path, segments)

    def test_configure_log_file_normal(self):
        """
        System test for using a file.
        """
        file_name, segments = self._getTempFilePath()
        content = (
            u'[log]\n'
            u'log_file: %s\n' % (file_name))
        log_id = factory.getUniqueInteger()
        log_message = factory.getUniqueString()

        configuration = self._getConfiguration(content=content)
        logger = factory.makeLogger()
        try:
            logger.configure(configuration)

            # Check logger configuration.
            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(isinstance(logger._file_handler, FileHandler))

            # Add two log entries and close the logger.
            logger.log(log_id, log_message)
            logger.log(log_id + 1, log_message)
            logger.shutdown()

            # Check that file exists and it has the right content.
            self.assertTrue(factory.fs.exists(segments))
            log_content = factory.fs.getFileContent(segments)
            self.assertEqual(2, len(log_content))
            self.assertStartsWith(str(log_id), log_content[0])
            self.assertEndsWith(log_message, log_content[0])
            self.assertStartsWith(str(log_id + 1), log_content[1])
        finally:
            factory.fs.deleteFile(segments)

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
        logger = factory.makeLogger()

        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(
                isinstance(logger._file_handler, WatchedFileHandler))
            logger.shutdown()
        finally:
            factory.fs.deleteFile(segments)

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
        logger = factory.makeLogger()

        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(
                isinstance(logger._file_handler, RotatingFileHandler))
            self.assertEqual(10, logger._file_handler.backupCount)
            logger.shutdown()
        finally:
            factory.fs.deleteFile(segments)

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
        logger = factory.makeLogger()
        try:
            logger.configure(configuration)

            self.assertIsNotNone(logger._file_handler)
            self.assertTrue(
                isinstance(logger._file_handler, TimedRotatingFileHandler))
            self.assertEqual(0, logger._file_handler.backupCount)
            self.assertEqual('H', logger._file_handler.when)
            self.assertEqual(2 * 60 * 60, logger._file_handler.interval)
            logger.shutdown()
        finally:
            factory.fs.deleteFile(segments)


class TestLoggerHandlers(ChevahTestCase):
    """
    Basic tests for handler(s) management.
    """
    def setUp(self):
        super(TestLoggerHandlers, self).setUp()
        log_name = factory.getUniqueString()
        self.logger = factory.makeLogger(log_name=log_name)

    def tearDown(self):
        self.logger.shutdown()
        super(TestLoggerHandlers, self).tearDown()

    def test_addHandler(self):
        """
        A LogHandler can be added to the logger and after that is called on
        all log events.
        """
        log_output = StringIO()
        log_handler = StreamHandler(log_output)
        log_entry_id = factory.getUniqueInteger()
        log_entry = factory.getUniqueString()

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
        log_entry_id = factory.getUniqueInteger()
        log_entry = factory.getUniqueString()

        self.logger.addHandler(log_handler)
        self.logger.removeHandler(log_handler)
        self.logger.log(log_entry_id, log_entry)
        handlers = self.logger.getHandlers()

        self.assertNotContains(log_handler, handlers)
        self.assertIsEmpty(handlers)
        self.assertIsEmpty(log_output.getvalue())
