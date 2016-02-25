"""All forms for extension."""

from django.forms import ModelForm
from django.utils.html import strip_tags

from .models import WebResource


class WebResourceForm(ModelForm):
    """Form for a single web resource."""

    def clean(self):
        """
        Clean additional data.

        Returns
        -------
        dict
            Cleaned data.
        """
        cleaned_data = super(WebResourceForm, self).clean()
        cleaned_data['name'] = strip_tags(cleaned_data['name'])
        cleaned_data['description'] = strip_tags(cleaned_data['description'])
        return cleaned_data

    class Meta:
        """Form meta."""

        model = WebResource
        fields = ('name', 'description', 'data_format', 'url', 'colour',
                  'symbol')
