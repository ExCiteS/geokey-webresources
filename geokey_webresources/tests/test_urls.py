"""All tests for URLs."""

from django.test import TestCase
from django.core.urlresolvers import reverse, resolve

from ..views import (
    IndexPage,
    AllWebResourcesPage,
    AddWebResourcePage,
    SingleWebResourcePage,
    RemoveWebResourcePage,
    ReorderWebResourcesAjax,
    UpdateWebResourceAjax,
    AllWebResourcesAPI,
    SingleWebResourceAPI
)


class UrlsTest(TestCase):
    """Test all URLs."""

    def test_index_page_reverse(self):
        """Test reverser for index page."""
        reversed_url = reverse('geokey_webresources:index')
        self.assertEqual(reversed_url, '/admin/webresources/')

    def test_index_page_resolve(self):
        """Test resolver for index page."""
        resolved_url = resolve('/admin/webresources/')
        self.assertEqual(resolved_url.func.__name__, IndexPage.__name__)

    def test_all_web_resources_page_reverse(self):
        """Test reverser for all web resources page."""
        reversed_url = reverse(
            'geokey_webresources:all_webresources',
            kwargs={'project_id': 1}
        )
        self.assertEqual(reversed_url, '/admin/projects/1/webresources/')

    def test_all_web_resources_page_resolve(self):
        """Test resolver for all web resources page."""
        resolved_url = resolve('/admin/projects/1/webresources/')
        self.assertEqual(
            resolved_url.func.__name__,
            AllWebResourcesPage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)

    def test_add_web_resource_page_reverse(self):
        """Test reverser for adding web resource page."""
        reversed_url = reverse(
            'geokey_webresources:webresource_add',
            kwargs={'project_id': 1}
        )
        self.assertEqual(reversed_url, '/admin/projects/1/webresources/add/')

    def test_add_web_resource_page_resolve(self):
        """Test resolver for adding web resource page."""
        resolved_url = resolve('/admin/projects/1/webresources/add/')
        self.assertEqual(
            resolved_url.func.__name__,
            AddWebResourcePage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)

    def test_single_web_resource_page_reverse(self):
        """Test reverser for single web resource page."""
        reversed_url = reverse(
            'geokey_webresources:single_webresource',
            kwargs={'project_id': 1, 'webresource_id': 5}
        )
        self.assertEqual(reversed_url, '/admin/projects/1/webresources/5/')

    def test_single_web_resource_page_resolve(self):
        """Test resolver for single web resource page."""
        resolved_url = resolve('/admin/projects/1/webresources/5/')
        self.assertEqual(
            resolved_url.func.__name__,
            SingleWebResourcePage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['webresource_id']), 5)

    def test_remove_web_resource_page_reverse(self):
        """Test reverser for removing web resource page."""
        reversed_url = reverse(
            'geokey_webresources:webresource_remove',
            kwargs={'project_id': 1, 'webresource_id': 5}
        )
        self.assertEqual(
            reversed_url,
            '/admin/projects/1/webresources/5/remove/'
        )

    def test_remove_web_resource_page_resolve(self):
        """Test resolver for removing web resource page."""
        resolved_url = resolve('/admin/projects/1/webresources/5/remove/')
        self.assertEqual(
            resolved_url.func.__name__,
            RemoveWebResourcePage.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['webresource_id']), 5)

    def test_reorder_web_resources_ajax_reverse(self):
        """Test reverser for reordering web resources Ajax."""
        reversed_url = reverse(
            'geokey_webresources:ajax_webresources_reorder',
            kwargs={'project_id': 1}
        )
        self.assertEqual(
            reversed_url,
            '/ajax/projects/1/webresources/reorder/'
        )

    def test_reorder_web_resources_ajax_resolve(self):
        """Test resolver for reordering web resources Ajax."""
        resolved_url = resolve('/ajax/projects/1/webresources/reorder/')
        self.assertEqual(
            resolved_url.func.__name__,
            ReorderWebResourcesAjax.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)

    def test_update_web_resource_ajax_reverse(self):
        """Test reverser for updating web resource Ajax."""
        reversed_url = reverse(
            'geokey_webresources:ajax_webresource_update',
            kwargs={'project_id': 1, 'webresource_id': 5}
        )
        self.assertEqual(
            reversed_url,
            '/ajax/projects/1/webresources/5/'
        )

    def test_update_web_resource_ajax_resolve(self):
        """Test resolver for updating web resource Ajax."""
        resolved_url = resolve('/ajax/projects/1/webresources/5/')
        self.assertEqual(
            resolved_url.func.__name__,
            UpdateWebResourceAjax.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['webresource_id']), 5)

    def test_all_web_resources_api_reverse(self):
        """Test reverser for all web resources API."""
        reversed_url = reverse(
            'geokey_webresources:api_all_webresources',
            kwargs={'project_id': 1}
        )
        self.assertEqual(
            reversed_url,
            '/api/projects/1/webresources/'
        )

    def test_all_web_resources_api_resolve(self):
        """Test resolver for all web resources API."""
        resolved_url = resolve('/api/projects/1/webresources/')
        self.assertEqual(
            resolved_url.func.__name__,
            AllWebResourcesAPI.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)

    def test_single_web_resource_api_reverse(self):
        """Test reverser for single web resource API."""
        reversed_url = reverse(
            'geokey_webresources:api_single_webresource',
            kwargs={'project_id': 1, 'webresource_id': 5}
        )
        self.assertEqual(reversed_url, '/api/projects/1/webresources/5/')

    def test_single_web_resource_api_resolve(self):
        """Test resolver for single web resource API."""
        resolved_url = resolve('/api/projects/1/webresources/5/')
        self.assertEqual(
            resolved_url.func.__name__,
            SingleWebResourceAPI.__name__
        )
        self.assertEqual(int(resolved_url.kwargs['project_id']), 1)
        self.assertEqual(int(resolved_url.kwargs['webresource_id']), 5)
