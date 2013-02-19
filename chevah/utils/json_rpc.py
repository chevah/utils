# Copyright (c) 2011 Adi Roiban.
# See LICENSE for details.
'''JSON-RPC 2.0 Twisted Web Resource.

An implemented JSON-RPC method will return a result that could be serialized
as JSON-RPC or raise an
'''

__metaclass__ = type

__all__ = []

import inspect
import simplejson as json
from twisted.internet import defer
from twisted.web import resource, server


def _parseError():
    '''Parse error response.'''
    message = 'Parse error.'
    return {'code': -32700, 'message': message, 'data': None}


def _invalidRequest(message=None):
    '''Invalid JSON-RPC request.'''
    if not message:
        message = 'Invalid request.'
    return {'code': -32600, 'message': message, 'data': None}


def _methodNotFound(message=None):
    '''Method not found.'''
    if not message:
        message = 'Method not found.'
    return {'code': -32601, 'message': message, 'data': None}


def _invalidArguments(message=None):
    '''Invalid parameters.'''
    if not message:
        message = 'Invalid parameters.'
    return {'code': -32602, 'message': message, 'data': None}


def _internalError(message=None):
    '''Internal error.'''
    if not message:
        message = 'Internal error.'
    return {'code': -32603, 'message': message, 'data': None}


def _noSessionError():
    '''Missing session error.'''
    # FIXME:698:
    # Move this out of commons as this is an server id.
    return {
        'code': 20100,
        'message': 'No session exists.',
        'data': None,
        }


class JSONRPCError(Exception):
    '''An error in processing an JSON-RPC.'''

    def __init__(self, value):
        self.value = value


class JSONRPCResource(resource.Resource, object):
    '''JSON-RPC 2.0 resource.'''

    isLeaf = True

    def __init__(self):
        super(JSONRPCResource, self).__init__()
        self.public_methods = []
        self._deferred = None

    def render_GET(self, request):
        '''Convert a GET request into an JSON-RPC request.'''
        # Remove trailing slash.
        if len(request.postpath) > 0 and request.postpath[-1] == '':
            request.postpath.pop()

        # Process index request
        if len(request.postpath) < 1:
            method_name = 'get_index'
        else:
            method_name = 'get_' + request.postpath[0]

        # Create the JSON-RPC request data.
        json_content = {
            'method': method_name,
            'params': {},
            'id': 1,
            'jsonrpc': 2.0,
            }
        return self._renderJSONRPCOverHTTP(request, json_content)

    def render_POST(self, request):
        '''Execute the requested JSON-RPC method.'''
        try:
            content = request.content.getvalue()
            json_content = json.loads(content)
        except json.decoder.JSONDecodeError:
            response = {'id': None, 'result': None, 'error': _parseError()}
            return json.dumps(response)

        return self._renderJSONRPCOverHTTP(request, json_content)

    def _renderJSONRPCOverHTTP(self, request, json_content):
        '''Execute the method and return a response for the HTTP request.

        Returns the JSON-RPC response or a defered with NOT_DONE_YET.
        '''
        # Check if we have a request id.
        # Notifications have no ID.
        # For notification the ID is set to None.
        try:
            request.id = json_content['id']
        except KeyError:
            json_content['id'] = None
            request.id = None

        try:
            json_content['jsonrpc']
        except KeyError:
            error_response = {
                'result': None,
                'error': _invalidRequest(u'Missing "jsonrpc".'),
                }
            return _getHTTPResponse(error_response, request)

        def _triggerRequest(request, json_content):
            '''Get and call the method inside a deferred.'''
            request_method = self._getMethod(json_content)
            result = self._callMethod(request_method, request, json_content)
            return result

        def _cbPackResult(result, request):
            return {'result': result, 'error': None}

        def _cbRender(result, request):
            '''Send the response.'''
            if request.id is None:
                # Do nothing for notifications.
                return
            response = _getHTTPResponse(result, request)
            request.write(response)
            request.finish()

        def _ebRenderJSONRPCError(failure, request):
            '''Send the error response or do nothing if the request is a
            notifcation.'''
            failure.trap(JSONRPCError)

            if request.id is None:
                # Do nothing for notifications.
                return

            result = {
                'result': None,
                'error': failure.value.value,
                }
            _cbRender(result, request)
            return None

        def _ebRenderInternalError(failure, request):
            '''Send the error response or do nothing if the request is a
            notifcation.'''

            if request.id is None:
                # Do nothing for notifications.
                return

            error_message = '%s - %s' % (
                failure.value, failure.getTraceback())
            self.logInternalError(error_message, peer=request.client)
            error = _internalError(
                message=u'Internal server error. %s' % (failure.value))

            result = {
                'result': None,
                'error': error,
                }
            _cbRender(result, request)

        # The deferred called is stored in the resourse so that we can
        # use it in tests.
        self._deferred = defer.maybeDeferred(
            _triggerRequest, request, json_content)
        self._deferred.addCallback(_cbPackResult, request)
        self._deferred.addCallback(_cbRender, request)
        self._deferred.addErrback(_ebRenderJSONRPCError, request)
        self._deferred.addErrback(_ebRenderInternalError, request)

        # For notification we return an empty response right away.
        # Request ID is None for notifications.
        if request.id is None:
            return ''
        else:
            return server.NOT_DONE_YET

    def _getMethod(self, json_content):
        '''Get the method for the JSON-RPC request.'''
        try:
            method_name = json_content['method']
        except KeyError:
            raise JSONRPCError(_invalidRequest(u'Missing "method".'))

        request_method = getattr(self, 'jsonrpc_' + method_name, None)
        if request_method is None:
            raise JSONRPCError(_methodNotFound())

        return request_method

    def _callMethod(self, request_method, request, json_content):
        '''Execute the JSON-RPC method.'''
        request.session = _get_session(request)
        if (request.session is None and
            not json_content['method'] in self.public_methods):
                raise JSONRPCError(_noSessionError())

        try:
            arguments = json_content['params']
        except KeyError:
            raise JSONRPCError(_invalidRequest(u'Missing "params".'))

        try:
            if type(arguments) is list:
                return _call_with_list(request_method, request, arguments)
            elif type(arguments) is dict:
                return _call_with_dict(request_method, request, arguments)
            else:
                raise JSONRPCError(
                    _invalidArguments(u'"params" must be list or dict.'))
        except JSONRPCError:
            # Reraise specific JSONRPC error as otherwise it will be
            # converted into internal server error.
            raise
        except:
            import traceback
            error_response = _internalError()
            error_details = traceback.format_exc()
            error_response.update({'data': error_details})
            self.logInternalError(error_details, peer=request.client)
            raise JSONRPCError(error_response)

    def logInternalError(self, details, peer=None):
        '''Log an internal error.

        This method can be overwritten to provide custom handling.
        '''
        raise NotImplementedError('Please define logInternalError.')


def _getHTTPResponse(result, request):
    '''Return the JSON-RPC result for an HTTP request.

    If 'jsonprc_result' is None it returns an empty result.
    '''
    if result is None:
        response_content = ''
    else:
        result.update({
            'jsonrpc': 2.0,
            'id': request.id,
            })
        response_content = json.dumps(result)

    request.setHeader("content-length", str(len(response_content)))
    request.setHeader("content-type", "text/json")
    return response_content


def _get_session(request):
    '''Return session or none if there is no session.'''
    for key, value in request.requestHeaders.getAllRawHeaders():
        if key.lower() == 'authorization':
            if not value:
                return None
            # The session is obtained from the site, and not the request,
            # since the request is using an HTTP cookie to retrieve the
            # session.
            return request.site.getSession(value[-1])
    return None


def _check_arguments(method, arguments):
    '''Check that arguments are valid to be called with method.'''
    method_arguments_spec = inspect.getargspec(method)
    argument_names = method_arguments_spec[0]
    default_values = method_arguments_spec[3]

    if default_values is None:
        default_values = ()

    number_or_mandatory_arguments = (
        len(argument_names) - 2 - len(default_values))

    if len(arguments) + 2 > len(argument_names):
        raise JSONRPCError(
            _invalidArguments(u'Too many values in "params".'))

    if len(arguments) < number_or_mandatory_arguments:
        raise JSONRPCError(
            _invalidArguments(u'Too few values in "params".'))

    # Check that all non-default arguments are present.
    if type(arguments) is dict:
        non_default_names = argument_names[2:(-1 * len(default_values))]
        for mandatory_argument in non_default_names:
            if mandatory_argument not in arguments:
                raise JSONRPCError(
                    _invalidArguments(
                        u'Bad values in "params".'))


def _get_result(method, request, *args, **kvargs):
    '''Simple wraper for formating an result.'''
    result = method(request, *args, **kvargs)
    return result


def _call_with_list(method, request, arguments):
    '''Call the method with list arguments.

    Raise JSONRPC error if arguments are not valid.
    '''
    _check_arguments(method, arguments)
    return _get_result(method, request, *arguments)


def _call_with_dict(method, request, arguments):
    '''Call the method with keyword arguments.

    Raise JSONRPC error if arguments are not valid.
    '''
    # Only str keys are accepted. Convert unicode to str.
    for key, value in arguments.items():
        del(arguments[key])
        arguments[str(key)] = value

    _check_arguments(method, arguments)
    return _get_result(method, request, **arguments)
