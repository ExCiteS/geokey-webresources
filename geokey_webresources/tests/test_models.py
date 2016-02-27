"""All tests for models."""

from django.test import TestCase

from nose.tools import raises

from geokey.projects.models import Project
from geokey.projects.tests.model_factories import ProjectFactory

from .model_factories import WebResourceFactory
from ..models import WebResource, post_save_project


class WebResourceTest(TestCase):
    """Test web resource model."""

    @raises(WebResource.DoesNotExist)
    def test_delete(self):
        """
        Test delete web resource.

        Web resource should still exist, but its status should be set to
        `deleted`.
        """
        webresource = WebResourceFactory.create()
        webresource.delete()
        WebResource.objects.get(pk=webresource.id)


class PostSaveProjectTest(TestCase):
    """Test post save of project."""

    @raises(WebResource.DoesNotExist)
    def test_post_save_project_when_deleting(self):
        """
        Test delete project.

        Web resources should also be removed.
        """
        project = ProjectFactory.create(status='active')
        webresource = WebResourceFactory.create(project=project)
        project.delete()

        post_save_project(Project, instance=project)

        WebResource.objects.get(pk=webresource.id)
