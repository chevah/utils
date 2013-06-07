# -*- coding: utf-8 -*-
'''Module containing helpers for testing the Chevah server.'''
from __future__ import with_statement

from StringIO import StringIO
import base64
import logging

from chevah.compat.testing import CompatManufacture
from chevah.utils.configuration_file import (
    FileConfigurationProxy,
    )
from chevah.utils.constants import (
    LOG_SECTION_DEFAULTS,
    )
from chevah.utils.credentials import (
    PasswordCredentials,
    FTPPasswordCredentials,
    FTPSPasswordCredentials,
    HTTPBasicAuthCredentials,
    HTTPSBasicAuthCredentials,
    SSHKeyCredentials,
    SSHPasswordCredentials,
    SSLCertificateCredentials,
    )
from chevah.utils.event import (
    EventDefinition,
    EventGroupDefinition,
    EventsDefinition,
    )
from chevah.utils.json_file import JSONFile
from chevah.utils.json_rpc import JSONRPCResource
from chevah.utils.logger import (
    _Logger,
    LogEntry,
    )
from chevah.utils.log_configuration_section import (
    LogConfigurationSection,
    )
from chevah.utils.observer import Signal


class UtilsManufacture(CompatManufacture):
    '''This class creates objects from chevah.utils module.

    It is designed to help with the tests and creating 'mock' objects.
    '''

    def Signal(self, *args, **kwargs):
        """
        Create a signal.
        """
        return Signal(*args, **kwargs)

    def _makeGenericPasswordCredentials(self,
            credentials_class,
            username=None, password=None, token=None,
            ):
        '''Create PasswordCredentials.'''
        if username is None:
            username = self.username
        else:
            username = unicode(username)

        if password is not None:
            password = unicode(password)

        credentials = credentials_class(
            username=username,
            password=password,
            )

        return credentials

    def makeFTPPasswordCredentials(self, *args, **kwargs):
        return self._makeGenericPasswordCredentials(
            FTPPasswordCredentials, *args, **kwargs)

    def makeFTPSPasswordCredentials(self, *args, **kwargs):
        return self._makeGenericPasswordCredentials(
            FTPSPasswordCredentials, *args, **kwargs)

    def makeSSHPasswordCredentials(self, *args, **kwargs):
        return self._makeGenericPasswordCredentials(
            SSHPasswordCredentials, *args, **kwargs)

    def makeHTTPBasicAuthCredentials(self, *args, **kwargs):
        return self._makeGenericPasswordCredentials(
            HTTPBasicAuthCredentials, *args, **kwargs)

    def makeHTTPSBasicAuthCredentials(self, *args, **kwargs):
        return self._makeGenericPasswordCredentials(
            HTTPSBasicAuthCredentials, *args, **kwargs)

    def makePasswordCredentials(self,
            username=None, password=None, token=None,
            ):
        '''Create PasswordCredentials.'''
        if username is None:
            username = self.getUniqueString()
        else:
            username = unicode(username)

        if password is not None:
            password = unicode(password)

        credentials = PasswordCredentials(
            username=username,
            password=password,
            )
        return credentials

    def makeSSHKeyCredentials(self,
            username=None,
            key=None,
            key_algorithm=None, key_data=None, key_signed_data=None,
            key_signature=None,
            *args, **kwargs
            ):

        if username is None:
            username = self.username
        else:
            username = unicode(username)

        if key is not None:
            key_parts = key.split()
            key_algorithm = key_parts[0]
            key_data = base64.decodestring(key_parts[1])

        credentials = SSHKeyCredentials(
            username=username,
            key_algorithm=key_algorithm,
            key_data=key_data,
            key_signed_data=key_signed_data,
            key_signature=key_signature,
            *args, **kwargs
            )

        return credentials

    def makeSSLCertificateCredentials(self,
            username=None,
            certificate=None,
            *args, **kwargs
            ):

        if username is None:
            username = self.username
        else:
            username = unicode(username)

        credentials = SSLCertificateCredentials(
            username=username,
            certificate=certificate,
            *args, **kwargs
            )

        return credentials

    def makeLogEntry(self):
        id = 100
        text = u'Entry content ' + self.getUniqueString()
        avatar = self.makeFilesystemApplicationAvatar()
        peer = self.makeIPv4Address()
        return LogEntry(
            message_id=id, text=text, avatar=avatar, peer=peer)

    def makeJSONRPCResource(self):
        '''Create a JSONRPCResource.'''
        return JSONRPCResource()

    def makeLogConfigurationSection(self, proxy=None):
        if proxy is None:
            content = (
                '[log]\n'
                'log_file: Disabled\n'
                'log_syslog: Disabled\n'
                )
            proxy = self.makeFileConfigurationProxy(
                content=content,
                defaults=LOG_SECTION_DEFAULTS,
                )

        return LogConfigurationSection(proxy=proxy)

    def makeFileConfigurationProxy(self, content=None, defaults=None):
        if content is None:
            content = ''
        proxy_file = FileConfigurationProxy(
            configuration_file=StringIO(content),
            defaults=defaults)
        proxy_file.load()
        return proxy_file

    def makeJSONFile(self, content=None, load=True):
        """
        Create a JSONFile.
        """
        json_file = JSONFile(file=StringIO(content))
        if load:
            json_file.load()
        return json_file

    def makeLogger(self, log_name=None):
        result = _Logger()

        if not log_name:
            log_name = self.getUniqueString()

        result._log = logging.getLogger(log_name)
        return result

    def makeEventGroupDefinition(self, name=None, description=None):
        """Creates an EventGroupDefinition."""
        if name is None:
            name = self.getUniqueString()
        if description is None:
            description = self.getUniqueString()

        event_group = EventGroupDefinition(name=name, description=description)

        return event_group

    def makeEventDefinition(self, id=None, message=None, groups=None,
            version_added=None, version_removed=None):
        """Creates an EventGroupDefinition."""
        if id is None:
            id = self.getUniqueString()
        if message is None:
            message = self.getUniqueString()

        event_definition = EventDefinition(
            id=id,
            message=message,
            groups=groups,
            version_added=version_added,
            version_removed=version_removed,
            )

        return event_definition

    def makeEventsDefinition(self,
            configuration_file=None, content=None,
            load=True,
            ):
        """Creates an EventHandler."""
        if configuration_file is None:
            if content is None:
                content = u''
            configuration_file = StringIO(content)

        config = EventsDefinition(file=configuration_file)

        if load:
            config.load()
        return config


manufacture = UtilsManufacture()
