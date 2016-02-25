"""All tests for context helpers."""

from django.test import TestCase

from ..helpers.context_helpers import does_not_exist_msg


class DoesNotExistMsgTest(TestCase):
    """Test does_not_exist_msg method."""

    def test_method(self):
        """Test with `Project`."""
        self.assertEqual(
            does_not_exist_msg('Project'),
            'Project matching query does not exist.'
        )
