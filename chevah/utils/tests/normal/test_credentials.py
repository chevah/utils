# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Tests for credentials used by Chevah project.
"""
from __future__ import with_statement

from chevah.empirical import ChevahTestCase, factory
from chevah.utils.credentials import (
    CredentialsBase,
    PasswordCredentials,
    SSHKeyCredentials,
    SSLCertificateCredentials,
    )


class TestCredentialsBase(ChevahTestCase):
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
        username = factory.getUniqueString()
        credentials = CredentialsBase(username=username)

        self.assertEqual(username, credentials.username)
        self.assertIsNone(credentials.peer)

    def test_kind_name(self):
        """
        If type name is request, a NotImplementedError is raises.
        """
        credentials = CredentialsBase(username=factory.getUniqueString())
        with self.assertRaises(NotImplementedError):
            credentials.kind_name


class TestPasswordCredentials(ChevahTestCase):
    """
    Tests for PasswordCredentials.
    """

    def test_init_default(self):
        """
        Check default valuse.
        """
        credentials = PasswordCredentials(username=factory.getUniqueString())
        self.assertIsNone(credentials.password)
        self.assertEqual(u'password', credentials.kind_name)

    def test_init_password_not_unicode(self):
        """
        AssertionError is raised if password is not unicode.
        """
        with self.assertRaises(AssertionError):
            PasswordCredentials(
                username=factory.getUniqueString(),
                password='a')

    def test_init_values(self):
        """
        Test initialization with values.

        We use any kind of values.
        """
        username = factory.getUniqueString()
        password = factory.getUniqueString()
        peer = factory.getUniqueString()
        credentials = PasswordCredentials(
            username=username,
            password=password,
            peer=peer,
            )
        self.assertEqual(username, credentials.username)
        self.assertEqual(password, credentials.password)
        self.assertEqual(peer, credentials.peer)


class TestSSHKeyCredentials(ChevahTestCase):
    """
    Tests for SSHKeyCredentials.
    """

    def test_init_default(self):
        """
        Check default values.
        """
        credentials = SSHKeyCredentials(username=factory.getUniqueString())
        self.assertIsNone(credentials.key_data)
        self.assertIsNone(credentials.key_algorithm)
        self.assertIsNone(credentials.key_signature)
        self.assertIsNone(credentials.key_signed_data)
        self.assertEqual(u'ssh key', credentials.kind_name)

    def test_init_values(self):
        """
        Check set values.
        """
        key_data = factory.getUniqueString()
        key_algorithm = factory.getUniqueString()
        key_signature = factory.getUniqueString()
        key_signed_data = factory.getUniqueString()
        credentials = SSHKeyCredentials(
            username=factory.getUniqueString(),
            key_data=key_data,
            key_signature=key_signature,
            key_algorithm=key_algorithm,
            key_signed_data=key_signed_data,
            )
        self.assertEqual(key_data, credentials.key_data)
        self.assertEqual(key_algorithm, credentials.key_algorithm)
        self.assertEqual(key_signature, credentials.key_signature)
        self.assertEqual(key_signed_data, credentials.key_signed_data)


class TestSSLCertificateCredentials(ChevahTestCase):
    """
    Tests for SSLCertificateCredentials.
    """

    def test_init_default(self):
        """
        Check default values.
        """
        credentials = SSLCertificateCredentials(
            username=factory.getUniqueString())
        self.assertIsNone(credentials.certificate)
        self.assertEqual(u'ssl certificate', credentials.kind_name)

    def test_init_values(self):
        """
        Check set values.
        """
        certificate = factory.getUniqueString()
        credentials = SSLCertificateCredentials(
            username=factory.getUniqueString(),
            certificate=certificate,
            )

        self.assertEqual(certificate, credentials.certificate)
