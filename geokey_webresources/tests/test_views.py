"""All tests for views."""

from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.test import TestCase
from django.template.loader import render_to_string
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site

from geokey import version
from geokey.core.tests.helpers import render_helpers, image_helpers
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from .model_factories import WebResourceFactory
from ..helpers.context_helpers import does_not_exist_msg
from ..base import FORMAT
from ..models import WebResource
from ..views import (
    IndexPage,
    AllWebResourcesPage,
    AddWebResourcePage,
    SingleWebResourcePage,
    RemoveWebResourcePage
)


no_rights_to_access_msg = 'You are not member of the administrators group ' \
                          'of this project and therefore not allowed to ' \
                          'alter the settings of the project'


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

    def test_get_non_existing(self):
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
            'symbol': image_helpers.get_image(file_name='test_wr_symbol.png')
        }

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

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

        rendered = render_to_string(
            'wr_add_webresource.html',
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
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'wr_add_webresource.html',
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
        self.request.method = 'GET'
        response = self.view(self.request, project_id=self.project.id).render()

        rendered = render_to_string(
            'wr_add_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
                'data_formats': FORMAT,
                'project': self.project
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            render_helpers.remove_csrf(response.content.decode('utf-8')),
            rendered
        )

    def test_get_non_existing(self):
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

        rendered = render_to_string(
            'wr_add_webresource.html',
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

    def test_post_with_anonymous(self):
        """
        Test POST with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        self.request.method = 'POST'
        self.request.POST = self.data
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_when_project_is_locked(self):
        """
        Test POST with with admin, when project is locked.

        It should inform user that the project is locked and redirect to add
        web resource page.
        """
        self.project.islocked = True
        self.project.save()

        self.request.user = self.admin
        self.request.method = 'POST'
        self.request.POST = self.data
        response = self.view(self.request, project_id=self.project.id)

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse(
                'geokey_webresources:add_webresource',
                kwargs={
                    'project_id': self.project.id
                }
            ),
            response['location']
        )
        self.assertEqual(WebResource.objects.count(), 0)


class SingleWebResourcePageTest(TestCase):
    """Test single web resource page."""

    def setUp(self):
        """Set up test."""
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
            'data_format': 'GeoJSON',
            'url': 'http://big-data.org.uk/test.json',
            'colour': '#000000',
            'symbol': image_helpers.get_image(file_name='test_wr_symbol.png')
        }

        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)

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

        rendered = render_to_string(
            'wr_single_webresource.html',
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

        rendered = render_to_string(
            'wr_single_webresource.html',
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

        rendered = render_to_string(
            'wr_single_webresource.html',
            {
                'GEOKEY_VERSION': version.get_version(),
                'PLATFORM_NAME': get_current_site(self.request).name,
                'user': self.request.user,
                'messages': get_messages(self.request),
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

    def test_get_non_existing(self):
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

        rendered = render_to_string(
            'wr_single_webresource.html',
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

    def test_post_with_anonymous(self):
        """
        Test POST with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        self.request.method = 'POST'
        self.request.POST = self.data
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_post_when_project_is_locked(self):
        """
        Test POST with with admin, when project is locked.

        It should inform user that the project is locked and redirect to the
        same web resource.
        """
        self.project.islocked = True
        self.project.save()

        self.request.user = self.admin
        self.request.method = 'POST'
        self.request.POST = self.data
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
        reference = WebResource.objects.get(pk=self.webresource.id)
        self.assertEqual(reference.name, self.webresource.name)
        self.assertEqual(reference.description, self.webresource.description)
        self.assertEqual(reference.data_format, self.webresource.data_format)
        self.assertEqual(reference.url, self.webresource.url)
        self.assertEqual(reference.colour, self.webresource.colour)
        self.assertEqual(reference.symbol, self.webresource.symbol)


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

    def test_get_non_existing(self):
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
