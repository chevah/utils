# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''Unit tests for JSON-RPC.'''

from __future__ import with_statement

from twisted.internet import defer
from twisted.web import server
import simplejson as json

from chevah.utils import json_rpc
from chevah.utils.json_rpc import JSONRPCResource, JSONRPCError
from chevah.utils.testing import manufacture, UtilsTestCase


class ImplementedJSONRPCResource(JSONRPCResource, object):
    '''A JSONRPC implementation for testing.'''

    def __init__(self):
        super(ImplementedJSONRPCResource, self).__init__()
        self.public_methods = [
            'public_notification',
            'public_notification_with_result',
            'public_method',
            'public_method_return_object',
            'public_method_no_arguments',
            'public_method_two_arguments',
            'public_method_two_arguments_one_default',
            'public_method_internal_error',
            'public_method_jsonrpc_error',
            'public_method_with_deferred',
            ]
        self._logInternalError_called = False
        self._logInternalError_value = None
        self._logInternalError_peer = None

    def logInternalError(self, value, peer=None):
        self._logInternalError_called = True
        self._logInternalError_value = value
        self._logInternalError_peer = peer

    def jsonrpc_get_index(self, request):
        return u'Index called'

    def jsonrpc_public_notification(self, request):
        return None

    def jsonrpc_public_notification_with_result(self, request):
        return u'Some result.'

    def jsonrpc_public_method(self, request):
        return u'public_method'

    def jsonrpc_public_method_return_object(self, request):
        return self.jsonrpc_public_method_return_object

    def jsonrpc_public_method_no_arguments(self, request):
        return u'public_method_no_arguments'

    def jsonrpc_public_method_two_arguments(self, request, one, two):
        return u'public_method_two_arguments'

    def jsonrpc_public_method_two_arguments_one_default(
            self, request, one, two=2):
        return u'public_method_two_arguments_one_default'

    def jsonrpc_public_method_internal_error(self, request):
        self._some_unknown = self._other_unknown
        return u'public_method_internal_error'

    def jsonrpc_public_method_jsonrpc_error(self, request):
        error = {
            'code': 42,
            'message': u'some-message',
            'data': u'some-data',
            }
        raise JSONRPCError(error)

    def jsonrpc_public_method_with_deferred(self, request):
        return defer.succeed('ok')

    def jsonrpc_private_method(self, request):
        return u'private_method'


class TestJSONRPC(UtilsTestCase):
    '''Test JSONRPC server.'''

    def _getDeferredResponse(self, data):
        '''Return the JSON-RPC response from deferred data.'''
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(
            resource=resource, data=data)
        result = resource.render_POST(request)
        self.assertEqual(server.NOT_DONE_YET, result)
        self.runDeferred(resource._deferred)
        return json.loads(request.test_response_content.decode('utf-8'))

    def test_POST_invalid_json(self):
        """
        An error is returned when posting a wrong formatted json.
        """
        data = '{bad-json,}'
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(
            resource=resource, data=data)
        response = json.loads(resource.render_POST(request))
        self.assertIsNone(response['result'])
        self.assertEqual(-32700, response['error']['code'])
        self.assertEqual(None, response['id'])

    def test_POST_no_version(self):
        """
        An error is raised when the request has no version.
        """
        data = '{"method": "some_method", "id": 2, "params": {}}'
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(
            resource=resource, data=data)
        response = json.loads(resource.render_POST(request).decode('utf-8'))
        self.assertIsNone(response['result'])
        self.assertEqual(-32600, response['error']['code'])
        self.assertEqual(u'Missing "jsonrpc".', response['error']['message'])
        self.assertEqual(2, response['id'])

    def _checkNotificationResult(self, data):
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(
            resource=resource, data=data)
        result = resource.render_POST(request)
        self.assertEqual('', result)

    def test_POST_notification_no_id(self):
        """
        All is ok if a notification has no id.
        """
        data = ('{"jsonrpc": "2.0", '
                '"method": "public_notification", "params": {}}')
        self._checkNotificationResult(data)

    def test_POST_notification_null_id(self):
        """
        All is ok if the notification has a null id.
        """
        data = ('{"jsonrpc": "2.0", "id": null,'
                '"method": "public_notification", "params": {}}')
        self._checkNotificationResult(data)

    def test_POST_notification_with_result(self):
        """
        Nothing is returned from a notification.
        """
        data = ('{"jsonrpc": "2.0", '
                '"method": "public_notification_with_result", "params": {}}')
        self._checkNotificationResult(data)

    def test_POST_missing_method(self):
        """
        An error is raised if no method was specified.
        """
        data = '{"jsonrpc": "2.0", "id": 1, "params": {}}'
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32600, response['error']['code'])
        self.assertEqual(u'Missing "method".', response['error']['message'])
        self.assertEqual(1, response['id'])

    def test_POST_missing_params(self):
        """
        An error is raised if no params are sent.
        """
        data = '{"jsonrpc": "2.0", "id": 1, "method": "public_method"}'
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32600, response['error']['code'])
        self.assertEqual(u'Missing "params".', response['error']['message'])
        self.assertEqual(1, response['id'])

    def test_POST_method_not_found(self):
        """
        An error is returned if method could not be found.
        """
        data = '{"jsonrpc": "2.0", "id": 1, "method": "nosuch", "params": {}}'
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32601, response['error']['code'])
        self.assertEqual(u'Method not found.', response['error']['message'])
        self.assertEqual(1, response['id'])

    def test_POST_no_session_with_private_method(self):
        """
        An error is returned when requesting a private method without a
        valid session.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "private_method", "params": {}}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(50000, response['error']['code'])
        self.assertEqual(1, response['id'])

    def test_POST_with_private_method(self):
        """
        Check requesting a private method with a valid session.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "private_method", "params": {}}')
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(
            resource=resource, data=data)
        session = request.getSession()
        request.setRequestHeader('authorization', session.uid)

        try:
            result = resource.render_POST(request)
            self.assertEqual(server.NOT_DONE_YET, result)
            self.runDeferred(resource._deferred)
            response = json.loads(
                request.test_response_content.decode('utf-8'))
            self.assertIsNone(response['error'])
            self.assertEqual(u'private_method', response['result'])
            self.assertEqual(1, response['id'])
        finally:
            session.expire()

    def test_POST_no_session_with_public_method(self):
        """
        Public method don't require a session.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 4, '
            '"method": "public_method", "params": {}}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['error'])
        self.assertEqual(u'public_method', response['result'])
        self.assertEqual(4, response['id'])

    def test_POST_public_method_return_object(self):
        """
        An error is raised if no JSON serializable data is returned.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "public_method_return_object", "params": {}}')

        response = self._getDeferredResponse(data)

        self.assertIsNone(response['result'])
        self.assertEqual(-32603, response['error']['code'])
        self.assertTrue(u'serializable' in response['error']['message'])
        self.assertEqual(1, response['id'])

    def test_POST_bad_params_type_string(self):
        """
        An error is raised when requesting an unknown parameter for a method.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "public_method", "params": "something"}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32602, response['error']['code'])
        self.assertEqual(1, response['id'])

    def test_POST_bad_params_to_many_array(self):
        """
        An error is raised if to many arguments are requested.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "public_method_no_arguments", "params": [1]}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32602, response['error']['code'])
        self.assertTrue(u'many' in response['error']['message'])
        self.assertEqual(1, response['id'])

    def test_POST_bad_params_to_few_array(self):
        """
        An error is raised if to few parameters are specified.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "public_method_two_arguments", "params": [1]}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32602, response['error']['code'])
        self.assertTrue(u'few' in response['error']['message'])
        self.assertEqual(1, response['id'])

    def test_POST_params_ok_default_array(self):
        """
        Default parameters are not requested.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, '
            '"method": "public_method_two_arguments_one_default", '
            '"params": [1]}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['error'])
        self.assertEqual(
            u'public_method_two_arguments_one_default', response['result'])
        self.assertEqual(1, response['id'])

    def test_POST_params_ok_default_dict(self):
        """
        Named parameters can be asked.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 2, '
            '"method": "public_method_two_arguments_one_default", '
            '"params": {"one": 1}}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['error'])
        self.assertEqual(
            u'public_method_two_arguments_one_default', response['result'])
        self.assertEqual(2, response['id'])

    def test_POST_params_ok_no_default_dict(self):
        """
        All is ok if all parameters are provided.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 4, '
            '"method": "public_method_two_arguments", '
            '"params": {"one": 1, "two": 2}}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['error'])
        self.assertEqual(
            u'public_method_two_arguments', response['result'])
        self.assertEqual(4, response['id'])

    def test_POST_params_bad_default_dict(self):
        """
        An error is raised if a parameter with a default value is not
        specified.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 5, '
            '"method": "public_method_two_arguments_one_default", '
            '"params": {"two": 2}}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32602, response['error']['code'])
        self.assertTrue('Bad values' in response['error']['message'])
        self.assertEqual(5, response['id'])

    def test_POST_params_unknown_dict(self):
        """
        An unknown named parameter will raise an error.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 4, '
            '"method": "public_method_two_arguments_one_default", '
            '"params": {"three": 3}}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(-32602, response['error']['code'])
        self.assertTrue(u'Bad values' in response['error']['message'])
        self.assertEqual(4, response['id'])

    def test_POST_internal_error(self):
        """
        Internal server errors are reported as errors.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 6, '
            '"method": "public_method_internal_error", "params": []}')

        resource = ImplementedJSONRPCResource()
        peer = manufacture.makeIPv4Address()
        request = manufacture.makeTwistedWebRequest(
            resource=resource, data=data, peer=peer)

        result = resource.render_POST(request)
        self.assertEqual(server.NOT_DONE_YET, result)
        self.runDeferred(resource._deferred)
        response = json.loads(request.test_response_content)

        self.assertIsNone(response['result'])
        self.assertEqual(-32603, response['error']['code'])
        self.assertEqual(6, response['id'])
        self.assertTrue(resource._logInternalError_called)
        self.assertTrue(u'internal' in resource._logInternalError_value)
        self.assertEqual(peer, resource._logInternalError_peer)

    def test_POST_jsonrpc_error(self):
        """
        An error is returned if the method raises a JSONRPCError.
        """
        data = (
            '{"jsonrpc": "2.0", "id": 4, '
            '"method": "public_method_jsonrpc_error", "params": []}')
        response = self._getDeferredResponse(data)
        self.assertIsNone(response['result'])
        self.assertEqual(42, response['error']['code'])
        self.assertEqual(u'some-message', response['error']['message'])
        self.assertEqual(u'some-data', response['error']['data'])
        self.assertEqual(4, response['id'])

    def test_GET_request(self):
        """
        A JSON-RCP method can also be requested using GET.
        """
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(resource=resource)
        request.postpath = ['method_name']
        # We monkey patch the renderJSONRPCOverHTTP since here we only
        # care about how a GET request is converted into a JSON-RPC
        # request. We don't really care about how it is process since
        # it will be checked in POST tests.
        resource._renderJSONRPCOverHTTP = lambda resource, json: json
        jsonrpc_request = resource.render_GET(request)
        self.assertEqual({}, jsonrpc_request['params'])
        self.assertEqual('get_method_name', jsonrpc_request['method'])
        self.assertEqual(1, jsonrpc_request['id'])
        self.assertEqual(2.0, jsonrpc_request['jsonrpc'])

    def test_GET_request_index(self):
        """
        By default GET on JSON-RCP will call get_index.
        """
        resource = ImplementedJSONRPCResource()
        request = manufacture.makeTwistedWebRequest(resource=resource)
        request.postpath = ['']

        # We monkey patch the renderJSONRPCOverHTTP since here we only
        # care about how a GET request is converted into a JSON-RPC
        # request. We don't really care about how it is process since
        # it will be checked in POST tests.
        resource._renderJSONRPCOverHTTP = lambda resource, json: json
        jsonrpc_request = resource.render_GET(request)
        self.assertEqual({}, jsonrpc_request['params'])
        self.assertEqual('get_index', jsonrpc_request['method'])
        self.assertEqual(1, jsonrpc_request['id'])
        self.assertEqual(2.0, jsonrpc_request['jsonrpc'])

    def test_POST_with_deferred(self):
        """
        JSON-RCP methods can return deferred(s).
        """
        data = (
            '{"jsonrpc": "2.0", "id": 1, "params": [], '
            '"method": "public_method_with_deferred"}')
        response = self._getDeferredResponse(data)
        self.assertIsNotNone(response['result'])
        self.assertEqual(u'ok', response['result'])
        self.assertEqual(1, response['id'])


class TestHelpers(UtilsTestCase):
    """
    Test JSON RPC helper methods.
    """
    def setUp(self):
        super(TestHelpers, self).setUp()
        self.request = manufacture.makeTwistedWebRequest()
        self.session = self.request.site.makeSession()

    def tearDown(self):
        if self.session:
            self.session.expire()
        super(TestHelpers, self).tearDown()

    def test_getSession_no_session(self):
        """
        None is returned if the request does not contain session
        information or the information is not valid.
        """
        session = json_rpc._get_session(self.request)

        self.assertIsNone(session)

        request = manufacture.makeTwistedWebRequest()
        request.setRequestHeader(
            'authorization', manufacture.getUniqueString())

        session = json_rpc._get_session(request)

        self.assertIsNone(session)

    def test_getSession_valid_session(self):
        """
        The session instance is returned if the request header contains
        valid session information.
        """
        self.request.setRequestHeader('authorization', self.session.uid)

        value = json_rpc._get_session(self.request)

        self.assertIsNotNone(value)
        self.assertEquals(self.session.uid, value.uid)
