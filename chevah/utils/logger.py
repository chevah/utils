# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Chevah logger.

The logger is based on Python logger.

All log messages are emitted using 'log' method.
Log levels are not used.

The logger can be configured to support various log handlers.
'''
from __future__ import with_statement

from logging import (
    FileHandler,
    getLogger,
    INFO,
    LogRecord,
    shutdown,
    StreamHandler,
    )
from logging.handlers import (
    RotatingFileHandler,
    SysLogHandler,
    TimedRotatingFileHandler,
    )

from stat import ST_DEV, ST_INO
import os
import sys
import time
import types

from chevah.compat.exceptions import (
    ChangeUserException,
    )
from chevah.utils.constants import (
    LOGGER_NAME,
    LOGGER_TIMESTAMP_FORMAT,
    )
from chevah.utils.exceptions import (
    UtilsError,
    )
from chevah.utils.helpers import _
from chevah.utils.observer import ObserverMixin, Signal

if os.name == 'nt':
    END_OF_LINE = '\r\n'
else:
    END_OF_LINE = '\n'


class LogEntry(LogRecord, object):
    '''An entry that will be received by all log handlers.'''

    def __init__(self, message_id, text, avatar=None, peer=None, data=None,
                timestamp=None):
        super(LogEntry, self).__init__(
            LOGGER_NAME,
            INFO,
            '(unknown file)',
            0,
            text,
            None,
            None,
            '(unknown function)',
            )
        self.message_id = message_id
        self.text = text
        self.avatar = avatar
        self.peer = peer
        self.data = data
        if timestamp is None:
            timestamp = time.time()
        self.timestamp = timestamp

    def __str__(self):
        return u'LogEntry(%s, %d, %s, avatar=%s, peer=%s)' % (
            self.timestamp_hr, self.message_id, self.text,
            self.avatar, self.peer)

    def __repr__(self):
        return self.__str__().encode('utf-8')

    @property
    def avatar_hr(self):
        '''Return the human readable string representation for the avatar
        name associated with this entry.

        If there is no account, it will return the u'None' string.
        '''
        if self.avatar:
            name = self.avatar.name
        else:
            name = u'None'

        return name

    @property
    def peer_hr(self):
        '''Return the human readable string representation for the
        peer socket associated with this entry.

        If there is no peer, it will return the u'None' string.
        '''

        if self.peer:
            peer_string = u'%s:%d' % (self.peer.host, self.peer.port)
        else:
            peer_string = u'None'
        return peer_string

    @property
    def timestamp_hr(self):
        '''The human readable representation for timestamp.'''
        return unicode(time.strftime(
            LOGGER_TIMESTAMP_FORMAT,
            time.localtime(self.timestamp,
            )))

    @property
    def service_hr(self):
        """
        The human readable representation for service name.
        """
        if self.data and 'server' in self.data:
            return self.data['service']
        else:
            return u'None'


class StdOutHandler(StreamHandler, object):
    """
    Prints all logs to standard output.

    Logs are not persisted.
    """

    def __init__(self):
        super(StdOutHandler, self).__init__()
        self.name = 'Standard output'

    def flush(self):
        '''Flushes the stream.'''
        if sys and sys.stdout:
            sys.stdout.flush()

    def emit(self, record):
        '''Emit a record.

        If a formatter is specified, it is used to format the record.
        The record is then written to the stream with a trailing newline
        [N.B. this may be removed depending on feedback]. If exception
        information is present, it is formatted using
        traceback.print_exception and appended to the stream.
        '''
        try:
            msg = self.format(record)
            format = '%s' + END_OF_LINE
            if not hasattr(types, 'UnicodeType'):  # if no unicode support...
                print(format % msg),
            else:
                try:
                    print(format % msg),
                except UnicodeError:
                    print(format % msg.encode('utf-8')),
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

if os.name == 'nt':
    from logging.handlers import NTEventLogHandler

    class WindowsEventLogHandler(NTEventLogHandler):
        """
        Custom NTEventLogger for logging Chevah events.

        For now we don't use any special category or level.
        """

        def getMessageID(self, log_entry):
            try:
                return int(log_entry.message_id)
            except:
                return 1
else:
    WindowsEventLogHandler = None


class _Logger(ObserverMixin):
    '''This class is supposed to be a singleton logger.'''

    NT_EVENTLOG_DDL = None
    NT_EVENTLOG_TYPE = 'Application'

    def __call__(self):
        '''Call method for implementing the singleton.'''
        return self

    def __init__(self):
        self._log = getLogger(LOGGER_NAME)
        self._log_stdout_handler = None
        self._log.setLevel(INFO)
        self._log_stdout_handler = None
        self._log_ntevent_handler = None
        self._new_handler_added = False
        self._configuration = None
        self._active_handlers = {
            'file': None,
            'syslog': None,
            'windows_eventlog': None,
            }

    def configure(self, configuration, account=None):
        """
        Setup logger based on the configuration file.

        After the logger is configured, remove the default standard out
        logger.

        All handler specific settings/configuration is passed via the settings
        parameter.
        """
        if self._configuration is not None:
            raise AssertionError(
                'For now, configure can only be called once.')

        self._configuration = configuration

        if account:
            try:
                from chevah.compat import system_users
                with system_users.executeAsUser(username=account):
                    self._configureHandlers()
            # FIXME:1050:
            # system_users.executeAsUser should raise a CompatError
            # instead of ChangeUserException.
            except ChangeUserException, error:
                raise UtilsError(u'1026', _(
                    u'Failed to initialize logger as account "%s". %s.)' % (
                        account, error.message)))
        else:
            self._configureHandlers()

        if self._new_handler_added:
            self._removeDefaultHandlers()

    def _configureHandlers(self):
        """
        Configure all handlers.
        """
        self._configuration.subscribe('file', self._reconfigureFile)
        self._configuration.subscribe(
            'file_rotate_external', self._reconfigureFile)
        self._configuration.subscribe(
            'file_rotate_count', self._reconfigureFile)
        self._configuration.subscribe(
            'file_rotate_at_size', self._reconfigureFile)
        self._configuration.subscribe(
            'file_rotate_each', self._reconfigureFile)
        self._active_handlers['file'] = self._addFile()

        self._configuration.subscribe('syslog', self._reconfigureSyslog)
        self._active_handlers['syslog'] = self._addSyslog()

        self._configuration.subscribe(
            'windows_eventlog', self._reconfigureWindowsEventLog)
        self._active_handlers['windows_eventlog'] = self._addWindowsEventLog()

    def _reconfigureHandler(self, name, setter):
        """
        Reconfigure handler with `name` using `setter` method.

        If adding the new handler fails, it will keep the previous
        handler.

        After successfully adding the handler, the previous handler is
        closed.
        """
        new_handler = None
        previous_handler = self._active_handlers[name]
        try:
            new_handler = setter()
        except:
            raise

        self._active_handlers[name] = new_handler
        self.removeHandler(previous_handler)

    def _reconfigureFile(self, signal):
        """
        Reconfigure the file handler.
        """
        self._reconfigureHandler(name='file', setter=self._addFile)

    def _reconfigureSyslog(self, signal):
        """
        Reconfigure the syslog handler.
        """
        self._reconfigureHandler(name='syslog', setter=self._addSyslog)

    def _reconfigureWindowsEventLog(self, signal):
        """
        Reconfigure the Windows Event handler.
        """
        self._reconfigureHandler(
            name='windows_eventlog', setter=self._addWindowsEventLog)

    def _addSyslog(self):
        """
        Add sending logs to Syslog using the configured value.

        Return the added handler, or `None.
        """
        syslog = self._configuration.syslog
        if not syslog:
            return None

        try:
            handler = SysLogHandler(
                syslog, facility=SysLogHandler.LOG_DAEMON)
            handler.name = u'Syslog at %s' % str(syslog)
        except Exception, error:
            raise UtilsError(u'1013',
                _(u'Failed to start the Syslog logger. %s' % (error)))

        self.addHandler(handler, patch_format=True)

        return handler

    def _addWindowsEventLog(self):
        """
        Add Windows Event handler if we are on Windows and it is enabled.

        Return the added handler, or `None`.
        """
        if not WindowsEventLogHandler:
            return

        source_name = self._configuration.windows_eventlog

        if not source_name:
            return

        try:
            handler = WindowsEventLogHandler(
                appname=source_name,
                dllname=self.NT_EVENTLOG_DDL,
                logtype=self.NT_EVENTLOG_TYPE,
                )
            handler.name = 'Windows Event as %s' % (source_name)
        except Exception, error:
            raise UtilsError(u'1014',
                _(u'Failed to start the Windows Event logger. %s' % (error)))
        self.addHandler(handler, patch_format=True)
        return handler

    def _addFile(self):
        """
        Add the a file logger using the configured value.

        Returns the added handler or `None` if no hander was added.
        """
        if not self._configuration.file:
            return

        from chevah.compat import local_filesystem
        log_path = os.path.abspath(
            local_filesystem.getEncodedPath(self._configuration.file))

        try:
            count = self._configuration.file_rotate_count
            bytes = self._configuration.file_rotate_at_size
            each = self._configuration.file_rotate_each

            if self._configuration.file_rotate_external:
                handler = WatchedFileHandler(
                    log_path, encoding='utf-8')
                handler.name = u'External rotated file %s' % (
                    self._configuration.file)
            elif each and each[0] > 0:
                interval_count, interval_type = each
                handler = TimedRotatingFileHandler(
                    log_path,
                    when=interval_type,
                    interval=interval_count,
                    backupCount=count,
                    encoding='utf-8',
                    )
                handler.name = (
                    u'Time base rotated file %s at %s keeping %s '
                    u'rotated archives' % (
                        self._configuration.file, each, count))
            elif bytes:
                handler = RotatingFileHandler(
                    log_path,
                    maxBytes=bytes,
                    backupCount=count,
                    encoding='utf-8',
                    )
                handler.name = (
                    u'Size base rotated file %s at %s bytes '
                    u'keeping %s rotated archives' % (
                        self._configuration.file, bytes, count))
            else:
                handler = FileHandler(log_path, encoding='utf-8')
                handler.name = u'File %s' % (self._configuration.file)

            self.addHandler(handler, patch_format=True)
        except Exception, error:
            raise UtilsError(u'1010',
                _(u'Failed to start the log file. %s' % (
                    unicode(error))))
        return handler

    def addDefaultStdOutHandler(self):
        """
        Add default handler for standard output.
        """
        self._log_stdout_handler = StdOutHandler()
        self.addHandler(self._log_stdout_handler, patch_format=True)

    def addDefaultWindowsEventLogHandler(self, source_name):
        """
        Add default handlers for windows event log.
        """
        self._log_ntevent_handler = WindowsEventLogHandler(source_name)
        self.addHandler(self._log_ntevent_handler, patch_format=True)

    def _removeDefaultHandlers(self):
        """
        Remove all default handlers.
        """
        self.removeHandler(self._log_stdout_handler)
        self.removeHandler(self._log_ntevent_handler)

    def log(self, message_id, text, avatar=None, peer=None, data=None):
        '''Log a message.'''
        self._log_helper(
            message_id=message_id,
            text=text,
            avatar=avatar,
            peer=peer,
            data=data,
            )

    def _log_helper(self, message_id, text, avatar=None, peer=None,
            data=None):
        '''This is here to help with testing, since log method is imported
        directly in all modules and we can not patch it.'''
        if avatar:
            peer = avatar.peer
        record = LogEntry(message_id, text, avatar, peer, data)
        self._log.handle(record)

    def debug(self, message):
        '''Log a debug message.

        This creates a dummy LogEntry with message_id 100.
        '''
        record = LogEntry(100, message)
        self._log.handle(record)

    def addHandler(self, handler, patch_format=False):
        """
        Add handler to the logger.

        If `patch_format` is True, the handler format logger, will be
        overwritten with the `format_log_entry` which converts an LogEntry
        into the string representation.
        """

        def format_log_entry(record):
            '''Return the string representation of a LogEntry.'''
            return u'%d %s %s %s %s %s' % (
                record.message_id,
                record.timestamp_hr,
                record.service_hr,
                record.avatar_hr,
                record.peer_hr,
                record.text,
                )

        if patch_format:
            handler.format = format_log_entry

        self._log.addHandler(handler)
        self._new_handler_added = True
        if handler.name:
            self.notify('add-handler', Signal(self, name=handler._name))

    def removeHandler(self, handler):
        """
        Remove specified handler from the logger and close it.
        """
        if not handler:
            return
        self._log.removeHandler(handler)
        handler.close()
        if handler.name:
            self.notify('remove-handler', Signal(self, name=handler._name))

    def removeAllHandlers(self):
        """
        Remove all handlers from the logger instance.
        """
        handlers = []
        handlers.extend(self.getHandlers())
        for handler in handlers:
            self.removeHandler(handler)

    def getHandlers(self):
        """
        Return a list with the active handlers.
        """
        return self._log.handlers

    @staticmethod
    def shutdown():
        '''Inform the main logging framework that we are going down.'''
        shutdown()


class WatchedFileHandler(FileHandler):
    """
    A handler for logging to a file, which watches the file
    to see if it has changed while in use. This can happen because of
    usage of programs such as newsyslog and logrotate which perform
    log file rotation. This handler, intended for use under Unix,
    watches the file to see if it has changed since the last emit.
    (A file has changed if its device or inode have changed.)
    If it has changed, the old file stream is closed, and the file
    opened to get a new stream.

    This handler is not appropriate for use under Windows, because
    under Windows open files cannot be moved or renamed - logging
    opens the files with exclusive locks - and so there is no need
    for such a handler. Furthermore, ST_INO is not supported under
    Windows; stat always returns zero for this value.

    This handler is based on a suggestion and patch by Chad J.
    Schroeder.
    """
    def __init__(self, filename, mode='a', encoding=None):
        FileHandler.__init__(self, filename, mode, encoding)
        if not os.path.exists(self.baseFilename):
            self.dev, self.ino = -1, -1
        else:
            stat = os.stat(self.baseFilename)
            self.dev, self.ino = stat[ST_DEV], stat[ST_INO]

    def emit(self, record):
        """
        Emit a record.

        First check if the underlying file has changed, and if it
        has, close the old stream and reopen the file to get the
        current stream.
        """
        if not os.path.exists(self.baseFilename):
            stat = None
            changed = True
        else:
            stat = os.stat(self.baseFilename)
            changed = (stat[ST_DEV] != self.dev) or (stat[ST_INO] != self.ino)
        if changed and self.stream is not None:
            self.stream.flush()
            self.stream.close()
            self.stream = self._open()
            if stat is None:
                stat = os.stat(self.baseFilename)
            self.dev, self.ino = stat[ST_DEV], stat[ST_INO]
        FileHandler.emit(self, record)


# Export Logger and log/debug as singletons.
Logger = _Logger()
log = Logger.log
debug = Logger.debug
