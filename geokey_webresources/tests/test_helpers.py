"""All tests for context helpers."""

from django.test import TestCase

from ..helpers.context_helpers import does_not_exist_msg


class DoesNotExistMsgTest(TestCase):
    """Test does_not_exist_msg method."""

    def test_method_with_project(self):
        """Test with `Project`."""
        self.assertEqual(
            does_not_exist_msg('Project'),
            'Project matching query does not exist.'
        )

    def test_method_with_webresource(self):
        """Test with `Web resource`."""
        self.assertEqual(
            does_not_exist_msg('Web resource'),
            'Web resource matching query does not exist.'
        )
