# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Tests for helpers.
"""
from OpenSSL import crypto
from mock import call

from chevah.utils.helpers import (
    generate_ssh_key,
    import_as_string,
    )
from chevah.utils.testing import UtilsTestCase


class DummyKey(object):
    """
    Helper for testing operations on SSH keys.
    """

    def __init__(self):
        self.generate = UtilsTestCase.Mock()
        self.store = UtilsTestCase.Mock()


class DummyOpenContext(object):
    """
    Helper for testing operations using open context manager.

    It keeps a record or all calls in self.calls.
    """

    def __init__(self):
        self.calls = []

    def __call__(self, path, mode):
        self.calls.append({'path': path, 'mode': mode})
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        return False


class TestHelpers(UtilsTestCase):
    """
    Tests for helpers.
    """

    def test_import_as_string_error(self):
        """
        Credentials must be initialized with at least the username.
        """
        with self.assertRaises(ImportError):
            import_as_string('no.such.module')

    def test_import_as_string_good(self):
        """
        Credentials must be initialized with at least the username.
        """
        module = import_as_string('chevah.utils')

        self.assertEqual('chevah.utils', module.__name__)

    def test_generate_ssh_key_default_values(self):
        """
        When no file and no comment is provided, it will use default
        values.
        """
        options = self.Bunch(
            key_size=1024,
            key_type=u'RSA',
            key_file=None,
            key_comment=None,
            )
        key = DummyKey()
        open_method = DummyOpenContext()

        exit_code, message = generate_ssh_key(
            options, key=key, open_method=open_method)

        # Key is generated with requested arguments.
        key.generate.assert_called_once_with(
            key_type=crypto.TYPE_RSA, key_size=1024)
        # Both private and public keys are stored.
        self.assertEqual(2, key.store.call_count)
        key.store.assert_has_calls([
            call(private_file=open_method),
            call(public_file=open_method, comment=None),
            ])
        # First is writes the private key.
        self.assertEqual(
            {'path': 'id_rsa', 'mode': 'wb'}, open_method.calls[0])
        # Then it writes the public key.
        self.assertEqual(
            {'path': 'id_rsa.pub', 'mode': 'wb'}, open_method.calls[1])
        self.assertEqual(
            u'SSH key of type "RSA" and length "1024" generated as public '
            u'key file "id_rsa.pub" and private key file "id_rsa" without '
            u'a comment.',
            message,
            )
        self.assertEqual(0, exit_code)

    def test_generate_ssh_key_with_comment(self):
        """
        When a comment is provided, it will be added to the public key file.
        """
        options = self.Bunch(
            key_size=1024,
            key_type=u'RSA',
            key_file=None,
            key_comment=u'this is a comment',
            )
        key = DummyKey()
        open_method = DummyOpenContext()

        exit_code, message = generate_ssh_key(
            options, key=key, open_method=open_method)

        # Writes the public key.
        self.assertEqual(
            {'path': 'id_rsa.pub', 'mode': 'wb'}, open_method.calls[1])
        self.assertContains(u'having comment "this is a comment"', message)
        self.assertEqual(0, exit_code)

    def test_generate_ssh_key_dsa(self):
        """
        When key type is DSA, it will generate DSA key.
        """
        options = self.Bunch(
            key_size=1024,
            key_type=u'DSA',
            key_file=None,
            key_comment=None,
            )
        key = DummyKey()
        open_method = DummyOpenContext()

        exit_code, message = generate_ssh_key(
            options, key=key, open_method=open_method)

        # Key is generated with requested arguments.
        key.generate.assert_called_once_with(
            key_type=crypto.TYPE_DSA, key_size=1024)
        # Both private and public keys are stored.
        self.assertEqual(2, key.store.call_count)
        # First is writes the private key.
        self.assertEqual(
            {'path': 'id_dsa', 'mode': 'wb'}, open_method.calls[0])
        # Then it writes the public key.
        self.assertEqual(
            {'path': 'id_dsa.pub', 'mode': 'wb'}, open_method.calls[1])
        self.assertContains(u'SSH key of type "DSA"', message)
        self.assertEqual(0, exit_code)

    def test_generate_ssh_key_file(self):
        """
        When a file name is provided, the key is generated having this name.
        """
        options = self.Bunch(
            key_size=1024,
            key_type=u'RSA',
            key_file=u'test_file',
            key_comment=None,
            )
        key = DummyKey()
        open_method = DummyOpenContext()

        exit_code, message = generate_ssh_key(
            options, key=key, open_method=open_method)

        # First is writes the private key.
        self.assertEqual(
            {'path': 'test_file', 'mode': 'wb'}, open_method.calls[0])
        # Then it writes the public key.
        self.assertEqual(
            {'path': 'test_file.pub', 'mode': 'wb'}, open_method.calls[1])
        self.assertContains(u'public key file "test_file.pub"', message)
        self.assertContains(u'private key file "test_file"', message)
        self.assertEqual(0, exit_code)
