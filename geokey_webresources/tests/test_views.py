"""All tests for views."""

from django.http import HttpRequest
from django.test import TestCase
from django.template.loader import render_to_string
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site

from geokey import version
from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from ..views import IndexPage


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
        Test get with with anonymous.

        It should redirect to login page.
        """
        self.request.user = AnonymousUser()
        response = self.view(self.request)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/account/login/', response['location'])

    def test_get_with_user(self):
        """
        Test get with with user.

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
                'user': user,
                'PLATFORM_NAME': get_current_site(self.request).name,
                'GEOKEY_VERSION': version.get_version(),
                'projects': projects
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'), rendered)
