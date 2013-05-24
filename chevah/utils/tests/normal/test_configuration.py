# Copyright (c) 2011-2013 Adi Roiban.
# See LICENSE for details.
"""
Test for property handling.
"""
from __future__ import with_statement

from chevah.utils.configuration import (
    ConfigurationSectionMixin,
    )
from chevah.utils.interfaces import (
    IConfigurationSection,
    )
from chevah.utils.testing import manufacture, UtilsTestCase


class TestConfigurationSectionMixin(UtilsTestCase):
    """
    Test for ConfigurationSectionMixin.
    """

    class DummyConfigurationSection(ConfigurationSectionMixin):
        """
        A dummy configuration section used to help with testing.
        """

        _section_name = 'section1'
        _prefix = 'sec'
        _parent = None

        def __init__(self, proxy=None):
            if proxy is None:
                self._proxy = manufacture.makeFileConfigurationProxy(
                    content='[section1]\nenabled: True\n')
            else:
                self._proxy = proxy

    def setUp(self):
        super(TestConfigurationSectionMixin, self).setUp()
        self.config = self.DummyConfigurationSection()

    def test_init(self):
        """
        Check initialization.
        """
        config = self.DummyConfigurationSection()
        self.assertProvides(IConfigurationSection, config)

    def test_enabled(self):
        """
        Enabled property is provided by the Mixin and it also emits
        signals on change.
        """
        call_list = []

        def notification(signal):
            call_list.append(signal)

        self.config.subscribe('enabled', notification)
        self.config.enabled = True
        self.assertIsTrue(self.config.enabled)

        self.config.enabled = False
        self.assertIsFalse(self.config.enabled)

        self.assertEqual(2, len(call_list))
        signal = call_list[1]
        self.assertIsTrue(signal.initial_value)
        self.assertIsFalse(signal.current_value)
        self.assertEqual(self.config, signal.source)
