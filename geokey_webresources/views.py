"""All views for extension."""

from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin

from geokey.core.decorators import handle_exceptions_for_admin
from geokey.projects.models import Project

from .helpers.context_helpers import does_not_exist_msg
from .models import WebResource


class IndexPage(LoginRequiredMixin, TemplateView):
    """Main index page."""

    template_name = 'wr_index.html'

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        all projects (where user is an administrator) to the context.

        Returns
        -------
        dict
            context
        """
        projects = Project.objects.get_list(self.request.user)
        projects = projects.filter(admins=self.request.user)

        return super(IndexPage, self).get_context_data(
            projects=projects,
            *args,
            **kwargs
        )


class AllWebResourcesPage(LoginRequiredMixin, TemplateView):
    """All web resources page."""

    template_name = 'wr_all_webresources.html'


class AddWebResourcePage(LoginRequiredMixin, TemplateView):
    """Add new web resource page."""

    template_name = 'wr_add_webresource.html'


class WebResourceMixin(LoginRequiredMixin, TemplateView):
    """Get web resource (and project) mixin."""

    @handle_exceptions_for_admin
    def get_context_data(self, project_id, webresource_id, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        a project and a web resource to the context.

        Returns
        -------
        dict
            context
        """
        self.project = Project.objects.as_admin(self.request.user, project_id)

        try:
            self.webresource = WebResource.objects.get(
                pk=webresource_id,
                project=self.project
            )

            return super(WebResourceMixin, self).get_context_data(
                project=self.project,
                webresource=self.webresource,
                *args,
                **kwargs
            )
        except WebResource.DoesNotExist:
            return {
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }


class SingleWebResourcePage(WebResourceMixin):
    """Single web resource page."""

    template_name = 'wr_single_webresource.html'


class RemoveWebResourcePage(WebResourceMixin):
    """Remove web resource page."""

    template_name = 'base.html'
