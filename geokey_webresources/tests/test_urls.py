"""All tests for URLs."""

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import IndexPage


class UrlsTest(TestCase):
    """Test all URLs."""

    def test_index_page_reverse(self):
        """Test reverser for index page."""
        reversed = reverse('geokey_webresources:index')
        self.assertEqual(reversed, '/admin/webresources/')

    def test_index_page_resolve(self):
        """Test resolver for index page."""
        resolved = resolve('/admin/webresources/')
        self.assertEqual(resolved.func.__name__, IndexPage.__name__)
