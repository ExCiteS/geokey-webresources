"""All tests for views."""

import os
import json

from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase, RequestFactory
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.test import APIRequestFactory, force_authenticate

from geokey import version
from geokey.core.tests.helpers import render_helpers, image_helpers
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from .model_factories import WebResourceFactory
from ..helpers.context_helpers import does_not_exist_msg
from ..base import STATUS, FORMAT
from ..models import WebResource
from ..forms import WebResourceForm
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


no_rights_to_access_msg = 'You are not member of the administrators group ' \
                          'of this project and therefore not allowed to ' \
                          'alter the settings of the project'


# ###########################
# TESTS FOR ADMIN PAGES
# ###########################

class IndexPageTest(TestCase):
    """Test index page."""

    def setUp(self):
        """Set up test."""
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.view = IndexPage.as_view()

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should render the page with all projects, where user is an
        administrator.
        """
        user = UserFactory.create()
        projects = [ProjectFactory.create(add_admins=[user])]

        ProjectFactory.create(add_contributors=[user])
        ProjectFactory.create()

        self.request.user = user
        response = self.view(self.request).render()

        rendered = render_to_string(
            'wr_index.html',
            {
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'user': self.request.user,
                'messages': get_messages(self.request),
                'projects': projects
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )


class AllWebResourcesPageTest(TestCase):
    """Test all web resources page."""

    def setUp(self):
        """Set up test."""
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.view = AllWebResourcesPage.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'wr_all_webresources.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'wr_all_webresources.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Permission denied.',
                'error_description': no_rights_to_access_msg
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should render the page with a project.
        """
        self.request.user = self.admin
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'wr_all_webresources.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'project': self.project
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that project does not exist.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id + 123
        ).render()

        rendered = render_to_string(
            'wr_all_webresources.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )


class AddWebResourcePageTest(TestCase):
    """Test add web resource page."""

    def setUp(self):
        """Set up test."""
        self.factory = RequestFactory()
        self.request = HttpRequest()
        self.view = AddWebResourcePage.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )

        self.data = {
            'name': 'Test Web Resource',
            'description': '',
            'data_format': 'GeoJSON',
            'url': 'http://big-data.org.uk/test.json',
            'colour': '#000000',
            'symbol': image_helpers.get_image(file_name='test_symbol.png')
        }
        self.url = reverse('geokey_webresources:webresource_add', kwargs={
            'project_id': self.project.id
        })

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def tearDown(self):
        """Tear down test."""
        for webresource in WebResource.objects.all():
            if webresource.symbol:
                webresource.symbol.delete()

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Permission denied.',
                'error_description': no_rights_to_access_msg
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should render the page with a project.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'data_formats': FORMAT,
                'project': self.project
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that project does not exist.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id + 123
        ).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project'),
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_post_with_anonymous(self):
        """
        Test POST with with anonymous.

        It should redirect to login page.
        """
        request = self.factory.post(self.url, self.data)
        request.user = AnonymousUser()

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_with_user(self):
        """
        Test POST with with user.

        It should not allow to add new web resources, when user is not an
        administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 0)

    def test_post_with_contributor(self):
        """
        Test POST with with contributor.

        It should not allow to add new web resources, when user is not an
        administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.contributor

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Permission denied.',
                'error_description': no_rights_to_access_msg
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 0)

    def test_post_with_admin(self):
        """
        Test POST with with admin.

        It should add new web resource, when user is an administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_webresources:all_webresources',
                kwargs={
                    'project_id': self.project.id
                }
            ),
            response['location']
        )
        self.assertEqual(WebResource.objects.count(), 1)

    def test_post_when_wrong_data(self):
        """
        Test POST with with admin, when data is wrong.

        It should inform user that data is wrong.
        """
        self.data['url'] = 'some web address'
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'data_formats': FORMAT,
                'project': self.project
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 0)

    def test_post_when_no_project(self):
        """
        Test POST with with admin, when project does not exist.

        It should inform user that project does not exist.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id + 123
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Project')
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 0)

    def test_post_when_project_is_locked(self):
        """
        Test POST with with admin, when project is locked.

        It should inform user that the project is locked.
        """
        self.project.islocked = True
        self.project.save()

        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(request, project_id=self.project.id).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'data_formats': FORMAT,
                'project': self.project
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 0)


class SingleWebResourcePageTest(TestCase):
    """Test single web resource page."""

    def setUp(self):
        """Set up test."""
        self.factory = RequestFactory()
        self.request = HttpRequest()
        self.view = SingleWebResourcePage.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.webresource = WebResourceFactory.create(project=self.project)

        self.data = {
            'name': self.webresource.name,
            'description': self.webresource.description,
            'data_format': 'KML',
            'url': 'http://big-data.org.uk/test.kml',
            'colour': '#000000',
            'symbol': image_helpers.get_image(file_name='test_symbol.png'),
            'clear-symbol': 'false'
        }
        self.url = reverse(
            'geokey_webresources:single_webresource',
            kwargs={
                'project_id': self.project.id,
                'webresource_id': self.webresource.id
            }
        )

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def tearDown(self):
        """Tear down test."""
        for webresource in WebResource.objects.all():
            if webresource.symbol:
                webresource.symbol.delete()

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should render the page with a project and web resource.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'status_types': STATUS,
                'data_formats': FORMAT,
                'project': self.project,
                'webresource': self.webresource
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that web resource does not exist.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id + 123,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_when_no_webresource(self):
        """
        Test GET with with admin, when web resource does not exist.

        It should inform user that web resource does not exist.
        """
        self.request.user = self.admin
        self.request.method = 'GET'
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id + 123
        ).render()

        form = WebResourceForm()
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_post_with_anonymous(self):
        """
        Test POST with with anonymous.

        It should redirect to login page.
        """
        request = self.factory.post(self.url, self.data)
        request.user = AnonymousUser()

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))

    def test_post_with_user(self):
        """
        Test POST with with user.

        It should not allow to update web resources, when user is not an
        administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.user

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))

    def test_post_with_contributor(self):
        """
        Test POST with with contributor.

        It should not allow to update web resources, when user is not an
        administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.contributor

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))

    def test_post_with_admin(self):
        """
        Test POST with with admin.

        It should update web resource, when user is an administrator.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_webresources:all_webresources',
                kwargs={
                    'project_id': self.project.id
                }
            ),
            response['location']
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.data.get('name'))
        self.assertEqual(reference.description, self.data.get('description'))
        self.assertEqual(reference.data_format, self.data.get('data_format'))
        self.assertEqual(reference.url, self.data.get('url'))
        self.assertEqual(reference.colour, self.data.get('colour'))
        self.assertTrue(bool(reference.symbol))

    def test_post_when_clearing_symbol(self):
        """
        Test POST with with admin, when clearing symbol.

        It should clear symbol from web resource.
        """
        self.webresource.symbol = image_helpers.get_image(
            file_name='test_symbol.png'
        )
        self.webresource.save()

        symbol = self.webresource.symbol.path

        self.data['clear-symbol'] = 'true'
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_webresources:all_webresources',
                kwargs={
                    'project_id': self.project.id
                }
            ),
            response['location']
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.data.get('name'))
        self.assertEqual(reference.description, self.data.get('description'))
        self.assertEqual(reference.data_format, self.data.get('data_format'))
        self.assertEqual(reference.url, self.data.get('url'))
        self.assertEqual(reference.colour, self.data.get('colour'))
        self.assertFalse(bool(reference.symbol))

        os.remove(symbol)

    def test_post_when_wrong_data(self):
        """
        Test POST with with admin, when data is wrong.

        It should inform user that data is wrong.
        """
        self.data['name'] = ''
        self.data['data_format'] = 'CSV'
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'status_types': STATUS,
                'data_formats': FORMAT,
                'project': self.project,
                'webresource': self.webresource
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))

    def test_post_when_no_project(self):
        """
        Test POST with with admin, when project does not exist.

        It should inform user that web resource does not exist.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id + 123,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))

    def test_post_when_no_webresource(self):
        """
        Test POST with with admin, when web resource does not exist.

        It should inform user that web resource does not exist.
        """
        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id + 123
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))

    def test_post_when_project_is_locked(self):
        """
        Test POST with with admin, when project is locked.

        It should inform user that the project is locked.
        """
        self.project.islocked = True
        self.project.save()

        request = self.factory.post(self.url, self.data)
        request.user = self.admin

        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        response = self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        form = WebResourceForm(data=self.data)
        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(request).name,
                'user': request.user,
                'messages': get_messages(request),
                'form': form,
                'status_types': STATUS,
                'data_formats': FORMAT,
                'project': self.project,
                'webresource': self.webresource
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertFalse(bool(reference.symbol))


class RemoveWebResourcePageTest(TestCase):
    """Test remove web resource page."""

    def setUp(self):
        """Set up test."""
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.view = RemoveWebResourcePage.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.webresource = WebResourceFactory.create(project=self.project)

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

    def test_get_with_anonymous(self):
        """
        Test GET with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.user
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 1)

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should not allow to access the page, when user is not an
        administrator.
        """
        self.request.user = self.contributor
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 1)

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should remove web resource and redirect to all web resources of a
        project.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_webresources:all_webresources',
                kwargs={'project_id': self.project.id}
            ),
            response['location']
        )
        self.assertEqual(WebResource.objects.count(), 0)

    def test_get_when_no_project(self):
        """
        Test GET with with admin, when project does not exist.

        It should inform user that web resource does not exist.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id + 123,
            webresource_id=self.webresource.id
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 1)

    def test_get_when_no_webresource(self):
        """
        Test GET with with admin, when web resource does not exist.

        It should inform user that web resource does not exist.
        """
        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id + 123
        ).render()

        rendered = render_to_string(
            'base.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )
        self.assertEqual(WebResource.objects.count(), 1)

    def test_get_when_project_is_locked(self):
        """
        Test GET with with admin, when project is locked.

        It should inform user that the project is locked and redirect the same
        web resource.
        """
        self.project.islocked = True
        self.project.save()

        self.request.user = self.admin
        response = self.view(
            self.request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_webresources:single_webresource',
                kwargs={
                    'project_id': self.project.id,
                    'webresource_id': self.webresource.id
                }
            ),
            response['location']
        )
        self.assertEqual(WebResource.objects.count(), 1)


# ###########################
# TESTS FOR ADMIN AJAX
# ###########################

class ReorderWebResourcesAjaxTest(TestCase):
    """Test reorder web resources via Ajax."""

    def setUp(self):
        """Set up test."""
        self.factory = APIRequestFactory()
        self.view = ReorderWebResourcesAjax.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.webresource_1 = WebResourceFactory.create(project=self.project)
        self.webresource_2 = WebResourceFactory.create(project=self.project)

        self.url = reverse(
            'geokey_webresources:ajax_webresources_reorder',
            kwargs={
                'project_id': self.project.id
            }
        )

    def _post(self, data, user):
        """Make test method for POST."""
        request = self.factory.post(
            self.url,
            data,
            content_type='application/json'
        )
        force_authenticate(request, user=user)

        return self.view(
            request,
            project_id=self.project.id
        ).render()

    def test_post_with_anonymous(self):
        """
        Test POST with with anonymous.

        It should return 404 response.
        """
        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            AnonymousUser()
        )

        self.assertEqual(response.status_code, 404)

        reference = self.project.webresources.all()
        self.assertEqual(reference[0].order, 0)
        self.assertEqual(reference[1].order, 0)

    def test_post_with_user(self):
        """
        Test POST with with user.

        It should return 404 response.
        """
        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            self.user
        )

        self.assertEqual(response.status_code, 404)

        reference = self.project.webresources.all()
        self.assertEqual(reference[0].order, 0)
        self.assertEqual(reference[1].order, 0)

    def test_post_with_contributor(self):
        """
        Test POST with with contributor.

        It should return 403 response.
        """
        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            self.contributor
        )

        self.assertEqual(response.status_code, 403)

        reference = self.project.webresources.all()
        self.assertEqual(reference[0].order, 0)
        self.assertEqual(reference[1].order, 0)

    def test_post_with_admin(self):
        """
        Test POST with with admin.

        It should return 200 response.
        """
        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            self.admin
        )

        self.assertEqual(response.status_code, 200)

        reference = self.project.webresources.all()
        self.assertEqual(reference[0], self.webresource_2)
        self.assertEqual(reference[1], self.webresource_1)

    def test_post_when_wrong_webresource_id(self):
        """
        Test POST with with admin, when web resource ID is wrong.

        It should return 400 response.
        """
        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id + 123
                ]
            }),
            self.admin
        )

        self.assertEqual(response.status_code, 400)

        reference = self.project.webresources.all()
        self.assertEqual(reference[0].order, 0)
        self.assertEqual(reference[1].order, 0)

    def test_post_when_no_project(self):
        """
        Test POST with with admin, when project does not exist.

        It should return 404 response.
        """
        self.project.delete()

        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            self.admin
        )

        self.assertEqual(response.status_code, 404)

    def test_post_when_no_webresources(self):
        """
        Test POST with with admin, when project has no web resources.

        It should return 404 response.
        """
        self.webresource_1.delete()
        self.webresource_2.delete()

        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            self.admin
        )

        self.assertEqual(response.status_code, 404)

    def test_post_when_project_is_locked(self):
        """
        Test POST with with admin, when project is locked.

        It should return 403 response.
        """
        self.project.islocked = True
        self.project.save()

        response = self._post(
            json.dumps({
                'order': [
                    self.webresource_2.id,
                    self.webresource_1.id
                ]
            }),
            self.admin
        )

        self.assertEqual(response.status_code, 403)

        reference = self.project.webresources.all()
        self.assertEqual(reference[0].order, 0)
        self.assertEqual(reference[1].order, 0)


class UpdateWebResourceAjaxTest(TestCase):
    """Test update web resource via Ajax."""

    def setUp(self):
        """Set up test."""
        self.factory = APIRequestFactory()
        self.view = UpdateWebResourceAjax.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.webresource = WebResourceFactory.create(
            status=STATUS.active,
            project=self.project
        )

        self.url = reverse(
            'geokey_webresources:ajax_webresource_update',
            kwargs={
                'project_id': self.project.id,
                'webresource_id': self.webresource.id
            }
        )

    def _put(self, data, user):
        """Make test method for PUT."""
        request = self.factory.put(self.url, data)
        force_authenticate(request, user=user)

        return self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

    def test_put_with_anonymous(self):
        """
        Test PUT with with anonymous.

        It should return 404 response.
        """
        response = self._put(
            {'status': 'inactive'},
            AnonymousUser()
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            WebResource.objects.get(pk=self.webresource.id).status,
            self.webresource.status
        )

    def test_put_with_user(self):
        """
        Test PUT with with user.

        It should return 404 response.
        """
        response = self._put(
            {'status': 'inactive'},
            self.user
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            WebResource.objects.get(pk=self.webresource.id).status,
            self.webresource.status
        )

    def test_put_with_contributor(self):
        """
        Test PUT with with contributor.

        It should return 403 response.
        """
        response = self._put(
            {'status': 'inactive'},
            self.contributor
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            WebResource.objects.get(pk=self.webresource.id).status,
            self.webresource.status
        )

    def test_put_with_admin(self):
        """
        Test PUT with with admin.

        It should return 200 response.
        """
        response = self._put(
            {'status': 'inactive'},
            self.admin
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WebResource.objects.get(pk=self.webresource.id).status,
            STATUS.inactive
        )

    def test_put_when_wrong_status(self):
        """
        Test PUT with with admin, when status is wrong.

        It should return 400 response.
        """
        response = self._put(
            {'status': 'wrong'},
            self.admin
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            WebResource.objects.get(pk=self.webresource.id).status,
            self.webresource.status
        )

    def test_put_when_no_project(self):
        """
        Test PUT with with admin, when project does not exist.

        It should return 404 response.
        """
        self.project.delete()

        response = self._put(
            {'status': 'inactive'},
            self.admin
        )

        self.assertEqual(response.status_code, 404)

    def test_put_when_no_webresource(self):
        """
        Test PUT with with admin, when web resource does not exist.

        It should return 404 response.
        """
        self.webresource.delete()

        response = self._put(
            {'status': 'inactive'},
            self.admin
        )

        self.assertEqual(response.status_code, 404)

    def test_put_when_project_is_locked(self):
        """
        Test PUT with with admin, when project is locked.

        It should return 403 response.
        """
        self.project.islocked = True
        self.project.save()

        response = self._put(
            {'status': 'inactive'},
            self.admin
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            WebResource.objects.get(pk=self.webresource.id).status,
            self.webresource.status
        )


# ###########################
# TESTS FOR PUBLIC API
# ###########################

class AllWebResourcesAPITest(TestCase):
    """Test all web resources API."""

    def setUp(self):
        """Set up test."""
        self.factory = APIRequestFactory()
        self.view = AllWebResourcesAPI.as_view()

        self.user = UserFactory.create()
        self.admin = UserFactory.create()
        self.contributor = UserFactory.create()
        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.webresource_1 = WebResourceFactory.create(
            status=STATUS.active,
            project=self.project
        )
        self.webresource_2 = WebResourceFactory.create(
            status=STATUS.inactive,
            project=self.project
        )

        self.url = reverse(
            'geokey_webresources:api_all_webresources',
            kwargs={
                'project_id': self.project.id
            }
        )

    def _get(self, user):
        """Make test method for GET."""
        request = self.factory.get(self.url)
        force_authenticate(request, user=user)

        return self.view(
            request,
            project_id=self.project.id
        ).render()

    def test_get_with_user(self):
        """
        Test GET with with user.

        It should return 404 response.
        """
        response = self._get(self.user)

        self.assertEqual(response.status_code, 404)

    def test_get_with_contributor(self):
        """
        Test GET with with contributor.

        It should return 200 response.
        """
        response = self._get(self.contributor)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['id'], self.webresource_1.id)

    def test_get_with_admin(self):
        """
        Test GET with with admin.

        It should return 200 response.
        """
        response = self._get(self.admin)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(len(content), 1)
        self.assertEqual(content[0]['id'], self.webresource_1.id)


class SingleWebResourceAPITest(TestCase):
    """Test single web resource API."""

    def setUp(self):
        """Set up test."""
        self.factory = APIRequestFactory()
        self.view = SingleWebResourceAPI.as_view()

        self.user = UserFactory.create()
        self.contributor = UserFactory.create()
        self.admin = UserFactory.create()

        self.project = ProjectFactory.create(
            add_admins=[self.admin],
            add_contributors=[self.contributor]
        )
        self.webresource = WebResourceFactory.create(
            status=STATUS.active,
            project=self.project
        )

        self.url = reverse(
            'geokey_webresources:api_single_webresource',
            kwargs={
                'project_id': self.project.id,
                'webresource_id': self.webresource.id
            }
        )

    def _get(self, user):
        """Make test GET method."""
        request = self.factory.get(self.url)
        force_authenticate(request, user=user)

        return self.view(
            request,
            project_id=self.project.id,
            webresource_id=self.webresource.id
        ).render()

    def test_get_with_user(self):
        """
        Test GET with user.

        Project is private and not everyone can contribute to it by default.

        It should return 404 response.
        """
        response = self._get(self.user)

        self.assertEqual(response.status_code, 404)

    def test_get_with_contributor(self):
        """
        Test GET with contributor.

        Contributors can access active web resources.

        It should return 200 response.
        """
        response = self._get(self.contributor)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(content['id'], self.webresource.id)

    def test_get_with_admin(self):
        """
        Test GET with admin.

        Admins can access active web resources.

        It should return 200 response.
        """
        response = self._get(self.admin)

        self.assertEqual(response.status_code, 200)

        content = json.loads(response.content)
        self.assertEqual(content['id'], self.webresource.id)

    def test_get_when_no_webresource(self):
        """
        Test GET with contributor and admin.

        It should return 404 response.
        """
        self.webresource.delete()

        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 404)

        response = self._get(self.admin)
        self.assertEqual(response.status_code, 404)

    def test_get_when_webresource_is_inactive(self):
        """
        Test GET with contributor and  admin.

        Inactive web resources cannot be accessed.

        It should return 404 response.
        """
        self.webresource.status = STATUS.inactive
        self.webresource.save()

        response = self._get(self.contributor)
        self.assertEqual(response.status_code, 404)

        response = self._get(self.admin)
        self.assertEqual(response.status_code, 404)
