# Copyright (c) 2011-2013 Adi Roiban.
# See LICENSE for details.
"""
The goal of this module is to provide a storage independent configuration
tree.

Property is any member of the configuration.
It can be:
* attribute - direct property
* section - property which has other properties
"""
from zope.interface import implements

from chevah.utils.interfaces import (
    IConfigurationSection,
    )
from chevah.utils.observer import Signal, ObserverMixin
from chevah.utils.property import PropertyMixin


class ConfigurationSectionMixin(
        ObserverMixin, PropertyMixin):
    """
    Mixin for a configuration section.
    """

    implements(IConfigurationSection)

    @property
    def enabled(self):
        '''Return True if service is enabled.'''
        return self._proxy.getBoolean(self._section_name, 'enabled')

    @enabled.setter
    def enabled(self, value):
        '''Set value for enable.'''
        initial = self.enabled
        self._proxy.setBoolean(
            self._section_name, 'enabled', value)
        signal = Signal(
            self, initial_value=initial, current_value=self.enabled)
        self.notify('enabled', signal)
