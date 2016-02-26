"""All views for extension."""

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.contrib import messages

from braces.views import LoginRequiredMixin

from geokey.projects.models import Project
from geokey.projects.views import ProjectContext

from .helpers.context_helpers import does_not_exist_msg
from .base import FORMAT
from .models import WebResource
from .forms import WebResourceForm


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


class AddWebResourcePage(LoginRequiredMixin, ProjectContext, CreateView):
    """Add new web resource page."""

    template_name = 'wr_add_webresource.html'
    form_class = WebResourceForm

    def get_context_data(self, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        available data formats to the context.

        Returns
        -------
        dict
            Context.
        """
        project_id = self.kwargs['project_id']

        return super(AddWebResourcePage, self).get_context_data(
            project_id,
            data_formats=FORMAT,
            *args,
            **kwargs
        )

    def form_valid(self, form):
        """
        Add web resource when form data is valid.

        Parameters
        ----------
        form : geokey_webresource.forms.WebResourceForm
            Represents the user input.

        Returns
        -------
        django.http.HttpResponse
            Rendered template.
        """
        context = self.get_context_data(form=form)
        project = context.get('project')

        if project:
            if project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. New web resources cannot be added.'
                )

            else:
                form.instance.project = project
                form.instance.creator = self.request.user

                add_another_url = reverse(
                    'geokey_webresources:webresource_add',
                    kwargs={
                        'project_id': project.id
                    }
                )
                messages.success(
                    self.request,
                    mark_safe(
                        'The web resource has been added. <a href="%s">Add '
                        'another web resource.</a>' % add_another_url
                    )
                )
                return super(AddWebResourcePage, self).form_valid(form)
        return self.render_to_response(context)

    def form_invalid(self, form):
        """
        Display an error message when form data is invalid.

        Parameters
        ----------
        form : geokey_webresource.forms.WebResourceForm
            Represents the user input.
        """
        messages.error(self.request, 'An error occurred.')
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """
        Set URL redirection when web resource created successfully.

        Returns
        -------
        string
            URL for redirection.
        """
        return reverse(
            'geokey_webresources:single_webresource',
            kwargs={
                'project_id': self.object.project.id,
                'webresource_id': self.object.id,
            }
        )


class WebResourceContext(LoginRequiredMixin, ProjectContext, TemplateView):
    """Get web resource mixin."""

    def get_context_data(self, project_id, webresource_id, *args, **kwargs):
        """
        GET method for the template.

        Return the context to render the view. Overwrite the method by adding
        a web resource and available data formats to the context.

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

        context['data_formats'] = FORMAT

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

    def get(self, request, project_id, webresource_id):
        """
        GET method for removing web resource.

        Parameter
        ---------
        request : django.http.HttpRequest
            Object representing the request.
        project_id : int
            Identifies the project in the database.
        webresource_id : int
            Identifies the web resource in the database.

        Returns
        -------
        django.http.HttpResponseRedirect
            Redirects to all web resources if web resource is removed, single
            web resource page if project is locked.
        django.http.HttpResponse
            Rendered template if project or web resource does not exist.
        """
        context = self.get_context_data(project_id, webresource_id)
        webresource = context.get('webresource')

        if webresource:
            if webresource.project.islocked:
                messages.error(
                    self.request,
                    'The project is locked. Web resource cannot be removed.'
                )
                return redirect(
                    'geokey_webresources:single_webresource',
                    project_id=project_id,
                    webresource_id=webresource_id
                )
            else:
                webresource.delete()

                messages.success(
                    self.request,
                    'The web resource has been removed.'
                )
                return redirect(
                    'geokey_webresources:all_webresources',
                    project_id=project_id
                )

        return self.render_to_response(context)
