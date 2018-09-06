# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_settings', '0003_customsettings_show_grades'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsettings',
            name='enable_enrollment_email',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='customsettings',
            name='show_grades',
            field=models.BooleanField(default=True),
        ),
    ]
