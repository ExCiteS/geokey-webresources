# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geokey_webresources', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webresource',
            name='symbol',
            field=models.ImageField(max_length=500, null=True, upload_to=b'webresources/symbols', blank=True),
        ),
    ]
