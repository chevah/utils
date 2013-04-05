# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Test for logger.'''

from __future__ import with_statement

from chevah.utils.constants import LOG_SECTION_DEFAULTS
from chevah.utils.testing import UtilsTestCase, manufacture
from chevah.utils.exceptions import UtilsError


class TestLogger(UtilsTestCase):
    """
    Tests for the logger.
    """

    def _getConfiguration(self, content=None):

        if not content:
            content = (
                '[log]\n'
                'log_file: Disabled\n'
                )
        proxy = manufacture.makeFileConfigurationProxy(
            content=content, defaults=LOG_SECTION_DEFAULTS)
        return manufacture.makeLogConfigurationSection(proxy=proxy)

    def test_configure_no_account(self):
        """
        Integration test that logger will raise an exception if
        account does not exists.
        """
        config = self._getConfiguration()
        account = u'no-such-account'
        logger = manufacture.makeLogger()

        with self.assertRaises(UtilsError) as context:
            logger.configure(configuration=config, account=account)

        self.assertEqual(u'1026', context.exception.event_id)

    def test_configure_logger_file_permissions_unix(self):
        """
        Integration test that the logger will initialize the log file
        using the account name.
        """
        path, segments = manufacture.fs.makePathInTemp()
        content = (
            '[log]\n'
            'log_file: %s\n'
            ) % (path)
        config = self._getConfiguration(content=content)
        if self._drop_user != '-':
            account = self._drop_user
        else:
            account = manufacture.username

        logger = manufacture.makeLogger()

        try:
            logger.configure(configuration=config, account=account)
            logger.removeAllHandlers()

            self.assertTrue(
                manufacture.fs.exists(segments),
                'Log file was not created at ' + path.encode('utf-8'),
                )

            # FIXME:928:
            # Rather than testing for 2 variables, we should only check
            # for matching "account" and not "Administrators".
            self.assertIn(
                [unicode(account), 'Administrators'],
                manufacture.fs.getOwner(segments))
        finally:
            manufacture.fs.deleteFile(segments, ignore_errors=True)
