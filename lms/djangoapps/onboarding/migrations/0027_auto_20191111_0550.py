# -*- coding: utf-8 -*-
# Generated by Django 1.11.21 on 2019-11-11 10:50
from __future__ import unicode_literals

import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0026_granteeoptin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluser',
            name='username',
            field=models.CharField(db_index=True, error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username'),
        ),
        migrations.AlterField(
            model_name='historicaluserextendedprofile',
            name='hours_per_week',
            field=models.PositiveIntegerField(default=0, null=True, validators=[django.core.validators.MaxValueValidator(168)], verbose_name=b'Typical Number of Hours Worked per Week*'),
        ),
        migrations.AlterField(
            model_name='userextendedprofile',
            name='hours_per_week',
            field=models.PositiveIntegerField(default=0, null=True, validators=[django.core.validators.MaxValueValidator(168)], verbose_name=b'Typical Number of Hours Worked per Week*'),
        ),
    ]
