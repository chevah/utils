# Copyright (c) 2012 Adi Roiban.
# See LICENSE for details.
"""
Tests for JSON file handling.
"""
from __future__ import with_statement
from StringIO import StringIO

from chevah.empirical import factory, EventTestCase

from chevah.utils.exceptions import ConfigurationError
from chevah.utils.json_file import JSONFile


class TestJSONFile(EventTestCase):
    """
    Tests for JSONFile.
    """

    def test_init_no_args(self):
        """
        AssertionError is raised if no arguments are specified.
        """
        with self.assertRaises(AssertionError):
            JSONFile()

    def test_init_both_args(self):
        """
        AssertionError is raised if both file and path are specified.
        """
        with self.assertRaises(AssertionError):
            JSONFile(path=u'some-path', file=StringIO())

    def test_init_good_path(self):
        """
        Everthing should be fine if initialized with a path.
        """
        path = factory.makeFilename()

        json_file = JSONFile(path=path)

        self.assertEqual(path, json_file.path)
        self.assertIsNone(json_file.file)

    def test_init_good_file(self):
        """
        Everthing should be fine if initialized with a file like object.
        """
        json_file = JSONFile(file=StringIO())

        self.assertIsNotNone(json_file.file)
        self.assertIsNone(json_file.path)

    def test_load_file_io_error(self):
        """
        An ConfigurationError is raised for any IO/OS Error.
        """
        path = factory.makeFilename()
        json_file = JSONFile(path=path)

        with self.assertRaises(ConfigurationError) as context:
            json_file.load()

        self.assertExceptionID(u'1027', context.exception)
        self.assertExceptionData(
            {
                u'path': path,
                u'details': self.Contains(u'No such file'),
            },
            context.exception,
            )

    def test_load_file_bad_format(self):
        """
        An ConfigurationError is raised for a bad formated JSON file.
        """
        content = '{ some-bad: "JSON"}'
        json_file = JSONFile(file=StringIO(content))

        with self.assertRaises(ConfigurationError) as context:
            json_file.load()

        self.assertExceptionID(u'1028', context.exception)
        self.assertExceptionData(
            {
                u'path': None,
                u'details': self.Contains(u'Expecting property'),
            },
            context.exception,
            )

    def test_load_file_good_format(self):
        """
        The parsed data will be available for read/write if it is valid.
        """
        string_value = factory.getUniqueString()
        content = '{ "some-good": 1, "utf8": "%s"}' % (string_value)
        json_file = JSONFile(file=StringIO(content))

        json_file.load()

        self.assertNotEqual({}, json_file.data)
        self.assertContains(u'some-good', json_file.data)
        self.assertEqual(1, json_file.data['some-good'])
        self.assertEqual(string_value, json_file.data['utf8'])

    def test_load_file_empty(self):
        """
        The parsed data will be available for read/write if it is valid.
        """
        json_file = JSONFile(file=StringIO(''))

        json_file.load()

        self.assertEqual(0, len(json_file.data))

    def test_getValueOrNone_none(self):
        """
        getValueOrNone will return `None` for disabled values.
        """
        content = '{ "some": "None", "blah": "Disabled", "deh": ""}'
        json_file = factory.makeJSONFile(content=content)

        self.assertIsNone(json_file.getValueOrNone(json_file.data, 'some'))
        self.assertIsNone(json_file.getValueOrNone(json_file.data, 'blah'))
        self.assertIsNone(json_file.getValueOrNone(json_file.data, 'deh'))

    def test_getValueOrNone_value(self):
        """
        getValueOrNone will return the actual value.
        """
        value = factory.getUniqueString()
        content = '{ "some": "%s"}' % (value)
        json_file = factory.makeJSONFile(content=content)

        self.assertEqual(
            value,
            json_file.getValueOrNone(json_file.data, 'some'),
            )

    def test_getValueOrNone_not_found(self):
        """
        getValueOrNone will raise AssertionError if key is not found.
        """
        content = '{ "some": "value"}'
        json_file = factory.makeJSONFile(content=content)

        with self.assertRaises(AssertionError):
            json_file.getValueOrNone(json_file.data, 'other')
