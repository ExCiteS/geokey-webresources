"""All helpers for the URL."""

import urllib2

from mimetypes import MimeTypes

from ..base import FORMAT
from ..exceptions import URLError


def check_url(url):
    """
    Check if URL is accessible and what data format it is.

    Parameters
    ----------
    url : str
        URL to check.

    Returns
    -------
    str
        Data format of the URL.
    """
    dataformat = None
    response = None
    errors = []

    try:
        response = urllib2.urlopen(url)
    except urllib2.URLError as error:
        if hasattr(error, 'code'):
            errors.append(
                'The server returned %s error.' % error.code
            )
        if hasattr(error, 'reason'):
            errors.append(
                'Failed to reach the server: %s.' % error.reason
            )

    if response:
        content_type = MimeTypes().guess_type(url)[0]

        if content_type == 'application/json':
            dataformat = FORMAT.GeoJSON
        elif content_type == 'application/vnd.google-earth.kml+xml':
            dataformat = FORMAT.KML
        elif content_type == 'application/gpx+xml':
            dataformat = FORMAT.GPX
        else:
            errors.append(
                'Data format `%s` is currently not supported.' % content_type
            )

    if errors:
        raise URLError('The URL cannot be used due to:', errors)

    return dataformat
