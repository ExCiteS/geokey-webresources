"""All URLs for extension."""

from django.conf.urls import url

from .views import IndexPage


urlpatterns = [
    url(
        r'^admin/webresources/$',
        IndexPage.as_view(),
        name='index')
]
