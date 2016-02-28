"""All serializers for extension."""

from rest_framework.serializers import SerializerMethodField

from geokey.core.serializers import FieldSelectorSerializer

from .models import WebResource


class WebResourceSerializer(FieldSelectorSerializer):
    """Serializer for web resource."""

    symbol = SerializerMethodField()

    def get_symbol(self, webresource):
        """
        Get URL of a symbol.

        Parameters
        ----------
        webresource : geokey_webresources.models.WebResource
            Web resource that is being serialised.
        """
        if webresource.symbol:
            return webresource.symbol.url

        return None

    class Meta:
        """Serializer meta."""

        model = WebResource
        fields = ('id', 'status', 'name', 'description', 'data_format', 'url',
                  'colour', 'symbol')