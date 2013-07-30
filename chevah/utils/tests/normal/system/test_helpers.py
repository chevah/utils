# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
System tests for helpers.
"""
from nose.plugins.attrib import attr

from chevah.utils.helpers import (
    generate_ssh_key,
    )
from chevah.utils.testing import mk, UtilsTestCase


class TestHelpers(UtilsTestCase):
    """
    Tests for helpers.
    """

    @attr('slow')
    def test_generate_ssh_key(self):
        """
        SSH key generation with custom key options.
        """
        file_path, private_segments = mk.fs.makePathInTemp()
        public_segments = private_segments[:]
        public_segments[-1] = u'%s.pub' % (public_segments[-1])
        options = object()
        # The current code don't allow creating smaller keys, so at 1024 bit,
        # this test is very slow.
        options = self.Bunch(
            key_size=1024,
            key_type='rsa',
            key_file=file_path,
            key_comment=u'%s %s' % (mk.string(), mk.string()),
            )
        self.assertFalse(mk.fs.exists(private_segments))
        self.assertFalse(mk.fs.exists(public_segments))

        try:
            exit_code, message = generate_ssh_key(options)

            self.assertTrue(mk.fs.exists(private_segments))
            self.assertTrue(mk.fs.exists(public_segments))
        finally:
            mk.fs.deleteFile(private_segments)
            mk.fs.deleteFile(public_segments)
        self.assertContains('type "rsa"',  message)
        self.assertContains('length "1024"', message)
        self.assertEqual(0, exit_code)
