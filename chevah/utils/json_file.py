# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Module for working with JSON files.
"""
from __future__ import with_statement

import simplejson as json

from chevah.utils.constants import (
    CONFIGURATION_DISABLED_VALUES,
    )
from chevah.utils.exceptions import UtilsError


class JSONFile(object):
    """
    A file containing JSON serialized data.

    This is a slightly modified version of JSON, which allow single line
    comments. A commented line should start with "# ", note the space after
    the "#".
    Inline comments are not supported.
    """

    def __init__(self, path=None, file=None):
        """
        It can be initialized with a path of a file like object.

        File like object initialization is mainly for testing.
        """
        from chevah.compat import local_filesystem
        self._path = path
        if self._path:
            self._segments = local_filesystem.getSegmentsFromRealPath(
                self._path)
        else:
            self._segments = None

        self._file = file
        if not (self._path or self._file) or (self._path and self._file):
            raise AssertionError('You must specify a path or a file.')

        self._data = {}

    @property
    def data(self):
        """
        Data stored by the JSONFile.
        """
        return self._data

    @property
    def path(self):
        """
        Path of this JSON file.
        """
        return self._path

    @property
    def file(self):
        """
        File object for this JSON file.
        """
        return self._file

    def load(self):
        """
        Load the JSON from input file. Deserialize data.
        """
        from chevah.compat import local_filesystem
        if self._segments:
            try:
                self._file = (
                    local_filesystem.openFileForReading(
                        self._segments, utf8=True))
            except IOError, error:
                data = {
                    'path': self._path,
                    'details': str(error),
                }
                raise UtilsError(u'1027',
                    u'Failed to load JSON file "%(path)s". %(details)s' % (
                        data),
                    data=data)

        try:
            result = json.load(self._file)
        except json.JSONDecodeError, error:
            if not error.doc:
                # If file is empty, just initialize an empty data structure.
                result = {}
            else:
                data = {
                    'path': self._path,
                    'details': str(error),
                }
                raise UtilsError(u'1028',
                    u'Bad format for JSON file "%(path)s". %(details)s' % (
                        data),
                    data=data)

        self._data = result

    def getValueOrNone(self, dictionary, key):
        """
        Return the value stored in `dictionary` at `key`.

        If no key is empty or key is disabled, it will return None.
        """
        if not key in dictionary:
            raise AssertionError(u'Dictionary has no key "%s".' % (key))

        value = dictionary[key]
        if value.lower() in CONFIGURATION_DISABLED_VALUES:
            return None
        elif len(value) == 0:
            return None
        else:
            return value
