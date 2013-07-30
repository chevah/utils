# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
System tests for helpers.
"""
from nose.plugins.attrib import attr

from chevah.utils.crypto import Key
from chevah.utils.helpers import (
    generate_ssh_key,
    )
from chevah.utils.testing import mk, UtilsTestCase


class TestHelpers(UtilsTestCase):
    """
    System tests for helpers.
    """

    @attr('slow')
    def test_generate_ssh_key_pair(self):
        """
        Private key pair is generated at specified path, and the public
        key is generated on a path based on private key path.
        """
        private_path, private_segments = mk.fs.makePathInTemp()
        public_path = u'%s.pub' % (private_path)
        public_segments = private_segments[:]
        public_segments[-1] = u'%s.pub' % (public_segments[-1])
        comment = u'%s %s' % (mk.string(), mk.string())
        options = object()
        # The current code don't allow creating smaller keys, so at 1024 bit,
        # this test is very slow.
        options = self.Bunch(
            key_size=1024,
            key_type='rsa',
            key_file=private_path,
            key_comment=comment,
            )
        self.assertFalse(mk.fs.exists(private_segments))
        self.assertFalse(mk.fs.exists(public_segments))

        try:
            generate_ssh_key(options)

            self.assertTrue(mk.fs.exists(private_segments))
            self.assertTrue(mk.fs.exists(public_segments))
            # Check content on private key.
            private_key = Key.fromFile(filename=private_path.encode('utf-8'))
            self.assertEqual(1024, private_key.size)
            self.assertIsFalse(private_key.isPublic())
            self.assertEqual('RSA', private_key.type())

            # Check content of public key.
            public_key = Key.fromFile(filename=public_path.encode('utf-8'))
            self.assertEqual(1024, public_key.size)
            self.assertIsTrue(public_key.isPublic())
            self.assertEqual('RSA', public_key.type())

            # Check that public key is the pair of private key.
            private_data = private_key.data()
            public_data = public_key.data()
            self.assertEqual(private_data['e'], public_data['e'])
            self.assertEqual(private_data['n'], public_data['n'])

        finally:
            mk.fs.deleteFile(private_segments)
            mk.fs.deleteFile(public_segments)
