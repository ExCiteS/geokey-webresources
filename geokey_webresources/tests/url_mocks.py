"""All URL mocks for tests."""

import urllib2

from StringIO import StringIO


def mock_responses(request, code, msg):
    """Mock responses."""
    response = urllib2.addinfourl(
        StringIO('mock file'),
        'mock message',
        request.get_full_url()
    )
    response.code = code
    response.msg = msg
    return response


class ValidURLHTTPHandler(urllib2.HTTPHandler):
    """Custom HTTP handler for a valid URL."""

    def http_open(self, request):
        """Mock response."""
        return mock_responses(request, 200, 'OK')


class InvalidURLHTTPHandler(urllib2.HTTPHandler):
    """Custom HTTP handler for a invalid URL."""

    def http_open(self, request):
        """Mock response."""
        return mock_responses(request, 404, 'NOT FOUND')
