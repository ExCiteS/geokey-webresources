"""All tests for serializers."""

from django.test import TestCase

from geokey.core.tests.helpers import image_helpers

from .model_factories import WebResourceFactory
from ..serializers import WebResourceSerializer


class WebResourceSerializerTest(TestCase):
    """Test web resource serializer."""

    def test_get_symbol(self):
        """Test getting correct URL for symbol."""
        webresource_1 = WebResourceFactory.create()
        webresource_2 = WebResourceFactory.create(
            symbol=image_helpers.get_image(file_name='test_serializer.png')
        )

        serializer = WebResourceSerializer(webresource_1)
        reference = serializer.get_symbol(webresource_1)
        self.assertIsNone(reference)

        serializer = WebResourceSerializer(webresource_2)
        reference = serializer.get_symbol(webresource_2)
        self.assertIn('test_serializer.png', reference)

        webresource_2.symbol.delete()
