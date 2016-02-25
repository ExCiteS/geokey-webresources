"""All models for extension."""

from django.conf import settings
from django.dispatch import receiver
from django.db import models

from model_utils.models import StatusModel, TimeStampedModel

from geokey.projects.models import Project

from .base import STATUS, FORMAT
from .managers import WebResourceManager


class WebResource(StatusModel, TimeStampedModel):
    """Store a single web resource."""

    STATUS = STATUS
    FORMAT = FORMAT

    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    data_format = models.CharField(max_length=10, null=False, choices=FORMAT)
    url = models.URLField(max_length=250)
    order = models.IntegerField(default=0)
    colour = models.TextField(default='#0033ff')
    symbol = models.ImageField(
        upload_to='webresources/symbols',
        null=True,
        max_length=500
    )

    project = models.ForeignKey(
        'projects.Project',
        related_name='webresources'
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL)

    objects = WebResourceManager()

    class Meta:
        """Model meta."""

        ordering = ['order']

    def delete(self):
        """
        Delete the web resource by setting its status to `deleted`.

        Notes
        -----
        It also deletes all contributions of that category.
        """
        self.status = self.STATUS.deleted
        self.save()


@receiver(models.signals.post_save, sender=Project)
def post_save_project(sender, instance, **kwargs):
    """
    Change status of web imports according to project's status.

    If project is set to `inactive`, make web resources `inactive` too. And if
    project is deleted, delete associated web resources.
    """
    webresources = WebResource.objects.filter(project=instance)

    if instance.status == 'inactive':
        webresources.update(status=WebResource.STATUS.inactive)
    elif instance.status == 'deleted':
        webresources.delete()
