"""All URLs for extension."""

from django.conf.urls import url

from .views import (
    IndexPage,
    AllWebResourcesPage,
    AddWebResourcePage,
    SingleWebResourcePage,
    RemoveWebResourcePage,
    ReorderWebResourcesAjax,
    UpdateWebResourceAjax
)


urlpatterns = [
    # ###########################
    # ADMIN PAGES
    # ###########################

    url(
        r'^admin/webresources/$',
        IndexPage.as_view(),
        name='index'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'webresources/$',
        AllWebResourcesPage.as_view(),
        name='all_webresources'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'webresources/add/$',
        AddWebResourcePage.as_view(),
        name='webresource_add'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'webresources/(?P<webresource_id>[0-9]+)/$',
        SingleWebResourcePage.as_view(),
        name='single_webresource'),
    url(
        r'^admin/projects/(?P<project_id>[0-9]+)/'
        r'webresources/(?P<webresource_id>[0-9]+)/remove/$',
        RemoveWebResourcePage.as_view(),
        name='webresource_remove'),

    # ###########################
    # ADMIN AJAX
    # ###########################

    url(
        r'^ajax/projects/(?P<project_id>[0-9]+)/'
        r'webresources/reorder/$',
        ReorderWebResourcesAjax.as_view(),
        name='ajax_webresources_reorder'),
    url(
        r'^ajax/projects/(?P<project_id>[0-9]+)/'
        r'webresources/(?P<webresource_id>[0-9]+)/$',
        UpdateWebResourceAjax.as_view(),
        name='ajax_webresource_update'),
]
