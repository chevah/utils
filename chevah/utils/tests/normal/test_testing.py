# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Tests for the testing infrastructure.

Stay tunes, the infinite loop is near...
'''
from __future__ import with_statement

from chevah.utils.testing import UtilsTestCase, manufacture


class TestFactory(UtilsTestCase):
    '''Test for factory methods.'''

    def test_credentials_unicode(self):
        """
        Make sure that credentials are created as unicode.
        """
        creds = manufacture.makePasswordCredentials(
            username='user',
            password='pass',
            token='don-t update',
            )
        self.assertTrue(type(creds.username) is unicode)
        self.assertTrue(type(creds.password) is unicode)
