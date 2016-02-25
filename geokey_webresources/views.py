"""All views for extension."""

from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin

from geokey.projects.models import Project


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


class SingleWebResourcePage(LoginRequiredMixin, TemplateView):
    """Single web resource page."""

    template_name = 'wr_single_webresource.html'


class RemoveWebResourcePage(LoginRequiredMixin, TemplateView):
    """Remove web resource page."""

    template_name = 'base.html'
