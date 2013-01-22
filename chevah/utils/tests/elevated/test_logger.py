# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Test for logger.'''

from __future__ import with_statement

from chevah.empirical import ChevahTestCase, factory
from chevah.utils.exceptions import (
    ConfigurationError,
    )


class TestLogger(ChevahTestCase):
    """
    Tests for the logger.
    """

    def _getConfiguration(self, content=None):

        if not content:
            content = (
                '[log]\n'
                'log_file: Disabled\n'
                )
        defaults = {
            'log_file': 'Disabled',
            'log_file_rotate_external': 'No',
            'log_file_rotate_at_size': 'Disabled',
            'log_file_rotate_each': 'Disabled',
            'log_file_rotate_count': 'Disabled',
            'log_syslog': 'Disabled',
            'log_sqlite': 'Disabled',
            'log_webadmin': 'Disabled',
            }
        proxy = factory.makeFileConfigurationProxy(
            content=content, defaults=defaults)
        return factory.makeLogConfigurationSection(proxy=proxy)

    def test_configure_no_services_account(self):
        """
        Integration test that logger will raise an exception if
        services_account does not exists.
        """
        config = self._getConfiguration()
        account = u'no-such-account'
        logger = factory.makeLogger()

        with self.assertRaises(ConfigurationError) as context:
            logger.configure(configuration=config, account=account)

        self.assertEqual(1026, context.exception.id)

    def test_configure_logger_file_permissions_unix(self):
        """
        Integration test that the logger will initialize the log file
        using the account name.
        """
        path, segments = factory.fs.makePathInTemp()
        content = (
            '[log]\n'
            'log_file: %s\n'
            ) % (path)
        config = self._getConfiguration(content=content)
        if self._drop_user != '-':
            account = self._drop_user
        else:
            account = factory.username

        logger = factory.makeLogger()

        try:
            logger.configure(configuration=config, account=account)
            logger.shutdown()

            self.assertTrue(
                factory.fs.exists(segments),
                'Log file was not created at ' + path.encode('utf-8'),
                )

            # FIXME:928:
            # Rather than testing for 2 variables, we should only check
            # for matching "account" and not "Administrators".
            self.assertIn(
                [unicode(account), 'Administrators'],
                factory.fs.getOwner(segments))
        finally:
            factory.fs.deleteFile(segments, ignore_errors=True)
