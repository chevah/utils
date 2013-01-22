'''Module for authentication related classes.'''
from __future__ import with_statement

__metaclass__ = type

from zope.interface import implements

from chevah.utils.interfaces import (
    ICredentials,
    IFTPPasswordCredentials,
    IFTPSPasswordCredentials,
    IFTPSSSLCertificateCredentials,
    IHTTPBasicAuthCredentials,
    IHTTPSBasicAuthCredentials,
    IHTTPSSSLCertificateCredentials,
    IPasswordCredentials,
    ISSHKeyCredentials,
    ISSHPasswordCredentials,
    ISSLCertificateCredentials,
    )


class CredentialsBase(object):
    """
    Base class for credentials used in the server.
    """

    implements(ICredentials)

    def __init__(self, username, peer=None):
        assert type(username) is unicode
        self.username = username
        self.peer = peer

    @property
    def kind_name(self):
        raise NotImplementedError()


class PasswordCredentials(CredentialsBase):
    """
    Credentials based on password.
    """
    implements(IPasswordCredentials)

    def __init__(self, password=None, token=None, *args, **kwargs):
        super(PasswordCredentials, self).__init__(*args, **kwargs)
        if password:
            assert type(password) is unicode
        self.password = password

    @property
    def kind_name(self):
        return u'password'


class HTTPBasicAuthCredentials(PasswordCredentials):
    """
    Marker class for password based credentials.

    HTTP Basic Auth credentials are username and password based.
    """
    implements(IHTTPBasicAuthCredentials)


class HTTPSBasicAuthCredentials(PasswordCredentials):
    '''Marker class for password based credentials.

    HTTPS Basic Auth credentials are username and password based.
    '''
    implements(IHTTPSBasicAuthCredentials)


class FTPPasswordCredentials(PasswordCredentials):
    '''Marker class for password based credentials used with FTP.'''
    implements(IFTPPasswordCredentials)


class FTPSPasswordCredentials(PasswordCredentials):
    '''Marker class for password based credentials used with FTPS.'''
    implements(IFTPSPasswordCredentials)


class SSHPasswordCredentials(PasswordCredentials):
    '''Marker class for password based credentials used with SFTP.'''
    implements(ISSHPasswordCredentials)


class SSHKeyCredentials(CredentialsBase):
    """
    A ssh key based credentials.
    """

    implements(ISSHKeyCredentials)

    def __init__(self,
            key_algorithm=None, key_data=None, key_signed_data=None,
            key_signature=None,
            *args, **kwargs
            ):
        super(SSHKeyCredentials, self).__init__(*args, **kwargs)
        self.key_algorithm = key_algorithm
        self.key_data = key_data
        self.key_signed_data = key_signed_data
        self.key_signature = key_signature

    @property
    def kind_name(self):
        return u'ssh key'


class SSLCertificateCredentials(CredentialsBase):
    """
    A SSL certificate key based credentials.
    """

    implements(ISSLCertificateCredentials)

    def __init__(self, certificate=None, *args, **kwargs):
        super(SSLCertificateCredentials, self).__init__(*args, **kwargs)
        self.certificate = certificate

    @property
    def kind_name(self):
        return u'ssl certificate'


class FTPSSSLCertificateCredentials(SSLCertificateCredentials):
    """
    A SSL certificate key based credentials for FTPS.
    """

    implements(IFTPSSSLCertificateCredentials)


class HTTPSSSLCertificateCredentials(SSLCertificateCredentials):
    """
    A SSL certificate key based credentials for HTTPS.
    """

    implements(IHTTPSSSLCertificateCredentials)
