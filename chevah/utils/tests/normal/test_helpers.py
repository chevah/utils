# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Tests for chevah commons helpers.
"""
from __future__ import with_statement

from chevah.empirical import ChevahTestCase
from chevah.utils.helpers import (
    import_as_string,
    )


class TestHelpers(ChevahTestCase):
    """
    Tests for helpers.
    """

    def test_import_as_string_error(self):
        """
        Credentials must be initialized with at least the username.
        """
        with self.assertRaises(ImportError):
            import_as_string('no.such.module')

    def test_import_as_string_good(self):
        """
        Credentials must be initialized with at least the username.
        """
        module = import_as_string('chevah.commons')

        self.assertEqual('chevah.commons', module.__name__)
