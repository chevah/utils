# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Chevah cryptography module.'''

__metaclass__ = type

from OpenSSL import crypto, rand
from Crypto.PublicKey import DSA, RSA
from twisted.conch.ssh.keys import Key as ConchSSHKey

from chevah.utils.constants import DEFAULT_KEY_SIZE
from chevah.utils.helpers import _
from chevah.utils.exceptions import UtilsError

__all__ = []
KEY_CLASSES = {
    crypto.TYPE_RSA: RSA,
    crypto.TYPE_DSA: DSA,
}


class Key(ConchSSHKey):
    '''A RSA or DSA key.'''

    def __init__(self, keyObject=None):
        super(Key, self).__init__(keyObject)

    def generate(self, key_type=crypto.TYPE_RSA, key_size=DEFAULT_KEY_SIZE):
        '''Create the key data.'''
        if key_type not in [crypto.TYPE_RSA, crypto.TYPE_DSA]:
            raise UtilsError(u'1003',
                _('Unknown key type "%s".' % (key_type)))

        key = None
        key_class = KEY_CLASSES[key_type]
        try:
            key = key_class.generate(bits=key_size, randfunc=rand.bytes)
        except ValueError, error:
            raise UtilsError(u'1004',
                _(u'Wrong key size "%d". %s.' % (key_size, unicode(error))))
        self.keyObject = key

    @property
    def size(self):
        '''Return the key size.'''
        return self.keyObject.size() + 1

    @property
    def private_openssh(self):
        '''Return the OpenSSH representation for the public key part.'''
        return self.toString(type='openssh')

    @property
    def public_openssh(self):
        '''Return the OpenSSH representation for private key part.'''
        return self.public().toString(type='openssh')

    def store(self,
            public_file=None, private_file=None, comment=None):
        '''Store the public and private key into a file.'''
        if public_file:
            if comment:
                public_content = '%s %s' % (
                    self.public_openssh, comment.encode('utf-8'))
            else:
                public_content = self.public_openssh
            public_file.write(public_content)
        if private_file:
            private_file.write(self.private_openssh)
