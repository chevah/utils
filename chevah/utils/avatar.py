# Copyright (c) 2010-2012 Adi Roiban.
# See LICENSE for details.
"""
An account as used by Chevah services.
"""
from chevah.utils import __python_future__
from copy import copy

from zope.interface import implements

from chevah.compat import HasImpersonatedAvatar
from chevah.utils.interfaces import IAvatarBase


class AvatarBase(HasImpersonatedAvatar):
    '''
    Base Avatar for all Chevah services.

    This avatar will be used by various adaptors to make it usable for each
    service.

    It should store all user configuration options.
    '''

    implements(IAvatarBase)

    def __init__(self, name, home_folder_path, root_folder_path=None,
            lock_in_home_folder=True, peer=None, token=None):
        self._name = name
        self._home_folder_path = home_folder_path
        self._root_folder_path = root_folder_path
        self._peer = peer
        self._token = token
        self._lock_in_home_folder = lock_in_home_folder

        assert type(self._home_folder_path) is unicode
        if self._root_folder_path:
            assert type(self._root_folder_path) is unicode

    def getCopy(self):
        """
        See: :class:`IAvatarBase`
        """
        result = copy(self)
        return result

    @property
    def token(self):
        """
        See: :class:`IAvatarBase`

        A token is only used for Windows accounts.
        """
        return self._token

    @property
    def home_folder_path(self):
        """
        See: :class:`IAvatarBase`
        """
        return self._home_folder_path

    @home_folder_path.setter
    def home_folder(self, value):
        self._home_folder_path = value

    @property
    def root_folder_path(self):
        """
        See: :class:`IAvatarBase`
        """
        return self._root_folder_path

    @root_folder_path.setter
    def root_folder_path(self, value):
        self._root_folder_path = value

    @property
    def lock_in_home_folder(self):
        """
        See: :class:`IAvatarBase`
        """
        return self._lock_in_home_folder

    @lock_in_home_folder.setter
    def lock_in_home_folder(self, value):
        self._lock_in_home_folder = value

    @property
    def name(self):
        '''Return avatar's name.'''
        return self._name

    @property
    def peer(self):
        """
        See: :class:`IAvatarBase`
        """
        return self._peer

    @peer.setter
    def peer(self, value):
        self._peer = value


class OSAvatar(AvatarBase):
    """
    Operating system avatar.
    """

    @property
    def use_impersonation(self):
        """
        See: :class:`IAvatarBase`

        For now OSAvatar is always be impersonated.
        """
        return True


class ApplicationAvatar(AvatarBase):
    """
    Application avatar.
    """

    @property
    def use_impersonation(self):
        """
        See: :class:`IAvatarBase`

        ApplicationAvatar can not be impersoanted.
        """
        return False
