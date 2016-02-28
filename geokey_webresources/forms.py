"""All forms for extension."""

from django.forms import ModelForm

from .models import WebResource


class WebResourceForm(ModelForm):
    """Form for a single web resource."""

    class Meta:
        """Form meta."""

        model = WebResource
        fields = ('name', 'description', 'data_format', 'url', 'colour',
                  'symbol')