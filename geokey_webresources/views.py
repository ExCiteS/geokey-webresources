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
