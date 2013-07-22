# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Various helpers for Chevah modules.

These code is here due to bad design. We should look for refactoring
the products so that this code is not needed.
'''
from __future__ import with_statement
from socket import gethostname
import sys
import threading
import urllib
import urlparse

from OpenSSL import crypto

from chevah.utils.constants import (
    DEFAULT_PUBLIC_KEY_EXTENSION,
    )
from chevah.utils.exceptions import (
    UtilsError,
    )


def _(string):
    '''Placeholder for future gettext integration.'''
    return string


def generate_ssh_key(options):
    '''Generate a SSH RSA or DSA key.

    Return a pair of (exit_code, operation_message).

    For success, exit_code is 0.
    '''
    from chevah.utils.crypto import Key
    exit_code = 0
    message = ''
    try:
        key_size = options.key_size

        if options.key_type.lower() == u'rsa':
            key_type = crypto.TYPE_RSA
        elif options.key_type.lower() == u'dsa':
            key_type = crypto.TYPE_DSA
        else:
            key_type = options.key_type

        if options.key_file is None:
            options.key_file = 'id_%s' % (options.key_type.lower())
        private_file = options.key_file

        public_file = u'%s%s' % (
            options.key_file, DEFAULT_PUBLIC_KEY_EXTENSION)

        key = Key()
        key.generate(key_type=key_type, key_size=key_size)

        with open(private_file, 'wb') as file_handler:
            key.store(private_file=file_handler)

        with open(public_file, 'wb') as file_handler:
            key.store(public_file=file_handler, comment=options.key_comment)

        if options.key_comment:
            comment = 'having comment "%s"' % (options.key_comment)
        else:
            comment = 'without a comment'

        message = (
            'SSH key of type "%s" and length "%d" generated as '
            'public key file "%s" and private key file "%s" %s.') % (
            options.key_type,
            key_size,
            public_file,
            private_file,
            comment,
            )

        exit_code = 0

    except UtilsError, error:
        exit_code = 1
        message = unicode(error)

    return (exit_code, message)


def generate_ssl_self_signed_certificate(options=None):
    '''Generate a self signed SSL certificate.

    Returns a tuple of (certificate_pem, key_pem)
    '''
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 1024)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "UN"
    cert.get_subject().ST = "Oceania"
    cert.get_subject().L = "Pitcairn Islands"
    cert.get_subject().O = "ACME Inc."
    cert.get_subject().OU = "Henderson"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha1')

    certificate_pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    key_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
    return (certificate_pem, key_pem)


def encode_unicode_url(url):
    '''Convert an unicode (or unicode encoded) url into an encoded URL.'''
    # turn string into unicode
    if not isinstance(url, unicode):
        url = url.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(url)

    # divide the netloc further
    userpass, at, hostport = parsed.netloc.partition('@')
    user, colon1, pass_ = userpass.partition(':')
    host, colon2, port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'), '')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).encode('utf8'), '=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).encode('utf8'))

    # put it back together
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urlparse.urlunsplit((scheme, netloc, path, query, fragment))


class TimeoutCommunicate(object):
    '''Helper class to execute the Popen.communicate using a timeout.

    process = Popen()
    try:
        timeout_communite = TimeoutCommunicate(process, 4)
    except TimeoutError:
        print 'Timeout'
    print timeout_communicate.output
    '''

    def __init__(self, process, timeout):
        self.output = None
        self._run(process, timeout)

    def _run(self, process, timeout):
        def target():
            self.output = process.communicate()

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.isAlive():
            raise UtilsError(u'1029',
                'Process executon timed out after "%s"', str(timeout))


class Bunch(object):
    """
    A simple class for collecting various things.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def import_as_string(module_name):
    """
    Import the module as dotted path string.
    """
    module_name = module_name.strip()
    __import__(module_name)
    return sys.modules[module_name]
