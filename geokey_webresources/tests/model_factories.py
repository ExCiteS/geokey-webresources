"""All model factories for tests."""

import factory

from geokey.users.tests.model_factories import UserFactory
from geokey.projects.tests.model_factories import ProjectFactory

from ..base import STATUS
from ..models import WebResource


class WebResourceFactory(factory.django.DjangoModelFactory):
    """Fake a single web resource."""

    status = STATUS.active

    name = factory.Sequence(lambda n: 'Web Resource %s' % n)
    description = factory.LazyAttribute(lambda o: '%s description.' % o.name)
    dataformat = 'GeoJSON'
    url = factory.Sequence(lambda n: 'https://domain.com/%d.json' % n)

    project = factory.SubFactory(ProjectFactory)
    creator = factory.SubFactory(UserFactory)

    class Meta:
        """Model factory meta."""

        model = WebResource
