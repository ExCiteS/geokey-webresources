# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-03-24 16:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geokey_webresources', '0002_auto_20160309_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webresource',
            name='dataformat',
            field=models.CharField(choices=[(b'GeoJSON', b'GeoJSON'), (b'KML', b'KML')], max_length=10),
        ),
    ]
