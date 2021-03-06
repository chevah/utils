# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Tests for credentials used by Chevah project.
"""
from __future__ import with_statement

from chevah.utils.testing import UtilsTestCase, manufacture
from chevah.utils.credentials import (
    CredentialsBase,
    PasswordCredentials,
    SSHKeyCredentials,
    SSLCertificateCredentials,
    )


class TestCredentialsBase(UtilsTestCase):
    """
    Tests for CredentialsBase.
    """

    def test_init_no_username(self):
        """
        Credentials must be initialized with at least the username.
        """
        with self.assertRaises(TypeError):
            CredentialsBase()

    def test_init_username_no_unicode(self):
        """
        AssertionError will be raised if username is not unicode.
        """
        with self.assertRaises(AssertionError):
            CredentialsBase('no-unicode')

    def test_init_default(self):
        """
        By default values for credentialsBase.
        """
        username = manufacture.getUniqueString()
        credentials = CredentialsBase(username=username)

        self.assertEqual(username, credentials.username)
        self.assertIsNone(credentials.peer)

    def test_kind_name(self):
        """
        If type name is request, a NotImplementedError is raises.
        """
        credentials = CredentialsBase(username=manufacture.getUniqueString())
        with self.assertRaises(NotImplementedError):
            credentials.kind_name


class TestPasswordCredentials(UtilsTestCase):
    """
    Tests for PasswordCredentials.
    """

    def test_init_default(self):
        """
        Check default valuse.
        """
        credentials = PasswordCredentials(
            username=manufacture.getUniqueString())
        self.assertIsNone(credentials.password)
        self.assertEqual(u'password', credentials.kind_name)

    def test_init_password_not_unicode(self):
        """
        AssertionError is raised if password is not unicode.
        """
        with self.assertRaises(AssertionError):
            PasswordCredentials(
                username=manufacture.getUniqueString(),
                password='a')

    def test_init_values(self):
        """
        Test initialization with values.

        We use any kind of values.
        """
        username = manufacture.getUniqueString()
        password = manufacture.getUniqueString()
        peer = manufacture.getUniqueString()
        credentials = PasswordCredentials(
            username=username,
            password=password,
            peer=peer,
            )
        self.assertEqual(username, credentials.username)
        self.assertEqual(password, credentials.password)
        self.assertEqual(peer, credentials.peer)


class TestSSHKeyCredentials(UtilsTestCase):
    """
    Tests for SSHKeyCredentials.
    """

    def test_init_default(self):
        """
        Check default values.
        """
        credentials = SSHKeyCredentials(
            username=manufacture.getUniqueString())
        self.assertIsNone(credentials.key_data)
        self.assertIsNone(credentials.key_algorithm)
        self.assertIsNone(credentials.key_signature)
        self.assertIsNone(credentials.key_signed_data)
        self.assertEqual(u'ssh key', credentials.kind_name)

    def test_init_values(self):
        """
        Check set values.
        """
        key_data = manufacture.getUniqueString()
        key_algorithm = manufacture.getUniqueString()
        key_signature = manufacture.getUniqueString()
        key_signed_data = manufacture.getUniqueString()
        credentials = SSHKeyCredentials(
            username=manufacture.getUniqueString(),
            key_data=key_data,
            key_signature=key_signature,
            key_algorithm=key_algorithm,
            key_signed_data=key_signed_data,
            )
        self.assertEqual(key_data, credentials.key_data)
        self.assertEqual(key_algorithm, credentials.key_algorithm)
        self.assertEqual(key_signature, credentials.key_signature)
        self.assertEqual(key_signed_data, credentials.key_signed_data)


class TestSSLCertificateCredentials(UtilsTestCase):
    """
    Tests for SSLCertificateCredentials.
    """

    def test_init_default(self):
        """
        Check default values.
        """
        credentials = SSLCertificateCredentials(
            username=manufacture.getUniqueString())
        self.assertIsNone(credentials.certificate)
        self.assertEqual(u'ssl certificate', credentials.kind_name)

    def test_init_values(self):
        """
        Check set values.
        """
        certificate = manufacture.getUniqueString()
        credentials = SSLCertificateCredentials(
            username=manufacture.getUniqueString(),
            certificate=certificate,
            )

        self.assertEqual(certificate, credentials.certificate)
