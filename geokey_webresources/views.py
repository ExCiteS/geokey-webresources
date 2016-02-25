"""All views for extension."""

from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin

from geokey.projects.models import Project
from geokey.projects.views import ProjectContext

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
            Context.
        """
        projects = Project.objects.filter(admins=self.request.user)

        return super(IndexPage, self).get_context_data(
            projects=projects,
            *args,
            **kwargs
        )


class AllWebResourcesPage(LoginRequiredMixin, ProjectContext, TemplateView):
    """All web resources page."""

    template_name = 'wr_all_webresources.html'


class AddWebResourcePage(LoginRequiredMixin, ProjectContext, TemplateView):
    """Add new web resource page."""

    template_name = 'wr_add_webresource.html'


class WebResourceContext(LoginRequiredMixin, ProjectContext, TemplateView):
    """Get web resource mixin."""

    def get_context_data(self, project_id, webresource_id, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        a web resource to the context.

        Returns
        -------
        dict
            Context.
        """
        context = super(WebResourceContext, self).get_context_data(
            project_id,
            *args,
            **kwargs
        )

        try:
            context['webresource'] = WebResource.objects.get(
                pk=webresource_id,
                project=context.get('project')
            )

            return context
        except WebResource.DoesNotExist:
            return {
                'error': 'Not found.',
                'error_description': does_not_exist_msg('Web resource')
            }


class SingleWebResourcePage(WebResourceContext):
    """Single web resource page."""

    template_name = 'wr_single_webresource.html'


class RemoveWebResourcePage(WebResourceContext):
    """Remove web resource page."""

    template_name = 'base.html'
