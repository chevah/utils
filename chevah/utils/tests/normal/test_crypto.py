# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Test module for crypto.'''
from __future__ import with_statement

from OpenSSL import crypto
from StringIO import StringIO

from nose.plugins.attrib import attr

from chevah.utils.crypto import Key
from chevah.utils.exceptions import UtilsError
from chevah.utils.testing import LogTestCase, mk

PUBLIC_RSA_ARMOR_START = u'-----BEGIN PUBLIC KEY-----\n'
PUBLIC_RSA_ARMOR_END = u'\n-----END PUBLIC KEY-----\n'
PRIVATE_RSA_ARMOR_START = u'-----BEGIN RSA PRIVATE KEY-----\n'
PRIVATE_RSA_ARMOR_END = u'\n-----END RSA PRIVATE KEY-----\n'
PUBLIC_DSA_ARMOR_START = u'-----BEGIN PUBLIC KEY-----\n'
PUBLIC_DSA_ARMOR_END = u'\n-----END PUBLIC KEY-----\n'
PRIVATE_DSA_ARMOR_START = u'-----BEGIN DSA PRIVATE KEY-----\n'
PRIVATE_DSA_ARMOR_END = u'\n-----END DSA PRIVATE KEY-----\n'

RSA_PRIVATE_KEY = (
'''-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQC4fV6tSakDSB6ZovygLsf1iC9P3tJHePTKAPkPAWzlu5BRHcmA
u0uTjn7GhrpxbjjWMwDVN0Oxzw7teI0OEIVkpnlcyM6L5mGk+X6Lc4+lAfp1YxCR
9o9+FXMWSJP32jRwI+4LhWYxnYUldvAO5LDz9QeR0yKimwcjRToF6/jpLwIDAQAB
AoGACB5cQDvxmBdgYVpuy43DduabTmR71HFaNFl+nE5vwFxUqX0qFOQpG0E2Cv56
zesPzT1JWBiqffSir4iSjH/lnskZnM9J1xfpnoJ5HTzcGHaBYVFEEXS6fOsyWT15
oY7Kb6rRBTnWV0Ins/05Hhp38r/RR/O4poB+3NwQJDl/6gECQQDoAnRdC+5SyjrZ
1JQUWUkapiYHIhFq6kWtGm3kWJn0IxCBtFhGvqIWJwZIAjf6tTKMUk6bjG9p7Jpe
tXUsTiDBAkEAy5EDU2F42Xm6tvQzM8bAgq7d2/x2iHRuOkDUb1bK3YwByTihl9BL
qvdRhRxpl21EcqWpB/RzAFbGa+60G/iV7wJABSz415KKkII+admaLBIJ1XRbaNFT
viTXxRLP3MY1OQMHPT1+sqVSDFh2hWi3QvqD1CmJ42JwodZLY018/a4IgQJAOsCg
yBjyyznB9PnoKUJs34rex5ZHE70e7zs01Omk5Wp6PXxVzz40CKUW5yc7JpRH1BsR
/RTFeEyTOiWL4CLQCwJAf4BF9eVLxRQ9A4Mm9Ikt4lF8ii6na4nxdtEzP8p2LP9t
LqHYUobNanxB+7Msi4f3gYyuKdOGnWHqD2U4HcLdMQ==
-----END RSA PRIVATE KEY-----''')

RSA_PUBLIC_KEY_OPENSSH = (
'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC4fV6tSakDSB6ZovygLsf1iC9P3tJHePTKAPkP'
'AWzlu5BRHcmAu0uTjn7GhrpxbjjWMwDVN0Oxzw7teI0OEIVkpnlcyM6L5mGk+X6Lc4+lAfp1YxCR'
'9o9+FXMWSJP32jRwI+4LhWYxnYUldvAO5LDz9QeR0yKimwcjRToF6/jpLw=='
)

DSA_PRIVATE_KEY = (
'''-----BEGIN DSA PRIVATE KEY-----
MIIBugIBAAKBgQDOwkKGnmVZ9bRl7ZCn/wSELV0n5ELsqVZFOtBpHleEOitsvjEB
BbTKX0fZ83vaMVnJFVw3DQSbi192krvk909Y6h3HVO2MKBRd9t29fr26VvCZQOxR
4fzkPuL+Px4+ShqE171sOzsuEDt0Mkxf152QxrA2vPowkj7fmzRH5xgDTQIVAIYb
/ljSUclo6TiNwoiF+9byafFJAoGAXA+TAGCmF2ZeNZN04mgxeyT34IAw37NGmLLP
/byi86dKcdz5htqPiOWcNmFzrA7a0o+erE3B+miwEm2sVz+eVWfNOCJQalHUqRrk
1iV542FL0BCePiJa91Baw4pVS5hnSNko/Wsp0VnW3q5OK/tPs1pRy+3qWUwwrg5i
zhYkBfwCgYB/6sL9MO4ZwtFzwbOKNOoZxfORwNbzzHf+IpzyBTxxQJcYS6QgbtSi
2tUY1WeJxmq/xkMoVLgpmpK6NN+NuB6aux54U7h5B3pZ7SnoRJ7vATQnMJpwZYno
8uZXhx4TmOoSxzxy2jTJb4rt4R6bbwjaI9ca/1iLavocQ218Zk204gIUTk7aRv65
oTedYsAyi80L8phYBN4=
-----END DSA PRIVATE KEY-----''')

DSA_PUBLIC_KEY_OPENSSH = (
'ssh-dss AAAAB3NzaC1kc3MAAACBAM7CQoaeZVn1tGXtkKf/BIQtXSfkQuypVkU60GkeV4Q6K2y+'
'MQEFtMpfR9nze9oxWckVXDcNBJuLX3aSu+T3T1jqHcdU7YwoFF323b1+vbpW8JlA7FHh/OQ+4v4/'
'Hj5KGoTXvWw7Oy4QO3QyTF/XnZDGsDa8+jCSPt+bNEfnGANNAAAAFQCGG/5Y0lHJaOk4jcKIhfvW'
'8mnxSQAAAIBcD5MAYKYXZl41k3TiaDF7JPfggDDfs0aYss/9vKLzp0px3PmG2o+I5Zw2YXOsDtrS'
'j56sTcH6aLASbaxXP55VZ804IlBqUdSpGuTWJXnjYUvQEJ4+Ilr3UFrDilVLmGdI2Sj9aynRWdbe'
'rk4r+0+zWlHL7epZTDCuDmLOFiQF/AAAAIB/6sL9MO4ZwtFzwbOKNOoZxfORwNbzzHf+IpzyBTxx'
'QJcYS6QgbtSi2tUY1WeJxmq/xkMoVLgpmpK6NN+NuB6aux54U7h5B3pZ7SnoRJ7vATQnMJpwZYno'
'8uZXhx4TmOoSxzxy2jTJb4rt4R6bbwjaI9ca/1iLavocQ218Zk204g=='
)


class TestKey(LogTestCase):
    '''Test Key generation and methods.'''

    def test_key_init_unknown_type(self):
        """
        An error is raised when generating a key with unknow type.
        """
        with self.assertRaises(UtilsError) as context:
            key = Key(None)
            key.generate(key_type=0)
        self.assertEqual(u'1003', context.exception.event_id)

    @attr('slow')
    def test_init_rsa(self):
        """
        Check generation of an RSA key.
        """
        key = Key()
        key.generate(key_type=crypto.TYPE_RSA, key_size=1024)
        self.assertEqual('RSA', key.type())
        self.assertEqual(1024, key.size)

    @attr('slow')
    def test_init_dsa(self):
        """
        Check generation of a DSA key.
        """
        key = Key()
        key.generate(key_type=crypto.TYPE_DSA, key_size=1024)
        self.assertEqual('DSA', key.type())
        self.assertEqual(1024, key.size)

    def test_key_store_rsa(self):
        """
        Check file serialization for a RSA key.
        """
        key = Key.fromString(data=RSA_PRIVATE_KEY)
        public_file = StringIO()
        private_file = StringIO()
        key.store(private_file=private_file, public_file=public_file)
        self.assertEqual(RSA_PRIVATE_KEY, private_file.getvalue())
        self.assertEqual(RSA_PUBLIC_KEY_OPENSSH, public_file.getvalue())

    def test_key_store_dsa(self):
        """
        Check file serialization for a DSA key.
        """
        key = Key.fromString(data=DSA_PRIVATE_KEY)
        public_file = StringIO()
        private_file = StringIO()
        key.store(private_file=private_file, public_file=public_file)
        self.assertEqual(DSA_PRIVATE_KEY, private_file.getvalue())
        self.assertEqual(DSA_PUBLIC_KEY_OPENSSH, public_file.getvalue())

    def test_key_store_comment(self):
        """
        When serializing a SSH public key to a file, a random comment can be
        added.
        """
        key = Key.fromString(data=RSA_PUBLIC_KEY_OPENSSH)

        public_file = StringIO()
        comment = mk.string()
        public_key_serialization = u'%s %s' % (
            RSA_PUBLIC_KEY_OPENSSH, comment)

        key.store(public_file=public_file, comment=comment)

        result_key = Key.fromString(public_file.getvalue())

        self.assertEqual(key.data, result_key.data)
        self.assertEqual(
            public_file.getvalue().decode('utf-8'), public_key_serialization)
