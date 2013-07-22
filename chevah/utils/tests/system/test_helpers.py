# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Tests for chevah commons helpers.
"""
from __future__ import with_statement

from chevah.utils.testing import mk, UtilsTestCase
from chevah.utils.helpers import (
    generate_ssh_key,
    )


class TestHelpers(UtilsTestCase):
    """
    Tests for helpers.
    """
    def test_generate_ssh_key(self):
        """
        Test SSH key generation with different key options.
        """
        options = object()
        options = self.Bunch(
            key_size=1024,
            key_type='rsa',
            key_file='test_file',
            key_comment=u'%s %s' % (mk.string(), mk.string()),
            )

        exit_code, message = generate_ssh_key(options)

        self.assertContains(str(options.key_size), message)
        self.assertContains(options.key_type, message)
        self.assertContains(options.key_file, message)
        self.assertContains(options.key_comment, message)
        self.assertEqual(0, exit_code)

    def test_generate_ssh_key_no_comment(self):
        """
        Test SSH key generation with different key options and no comment.
        """
        options = object()
        options = self.Bunch(
            key_size=1024,
            key_type='rsa',
            key_file='test_file',
            key_comment='',
            )
        no_key_comment_text = u'without a comment'

        exit_code, message = generate_ssh_key(options)

        self.assertContains(str(options.key_size), message)
        self.assertContains(options.key_type, message)
        self.assertContains(options.key_file, message)
        self.assertContains(no_key_comment_text, message)
        self.assertEqual(0, exit_code)
