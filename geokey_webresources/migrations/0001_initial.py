# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0007_auto_20160122_1409'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('status', model_utils.fields.StatusField(default=b'active', max_length=100, verbose_name='status', no_check_for_status=True, choices=[(b'active', b'active'), (b'inactive', b'inactive'), (b'deleted', b'deleted')])),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, verbose_name='status changed', monitor='status')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('data_format', models.CharField(max_length=10, choices=[(b'GeoJSON', b'GeoJSON'), (b'KML', b'KML'), (b'GPX', b'GPX')])),
                ('url', models.URLField(max_length=250)),
                ('order', models.IntegerField(default=0)),
                ('colour', models.TextField(default=b'#0033ff')),
                ('symbol', models.ImageField(max_length=500, null=True, upload_to=b'webresources/symbols')),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(related_name='webresources', to='projects.Project')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
