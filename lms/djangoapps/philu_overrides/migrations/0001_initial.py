# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, connection

#TODO: find a more better way of handling history of builtin packages
class Migration(migrations.Migration):
    dependencies = [
        ('enterprise', '0009_auto_20161130_1651'),
    ]

    def add_history_columns(apps, schema_editor):
        cursor = connection.cursor()
        tables = [
            'enterprise_historicalenterprisecustomer',
            'enterprise_historicalenterprisecustomerentitlement',
            'enterprise_historicalenterprisecourseenrollment',
            'enterprise_historicalenterprisecustomercatalog',
            'enterprise_historicalenrollmentnotificationemailtemplate',
            'consent_historicaldatasharingconsent',
            'degreed_historicaldegreedenterprisecustomerconfiguration'
        ]
        for t in tables:
            query = 'ALTER TABLE %s ADD start_date DATETIME NULL, ADD end_date DATETIME NULL;' % t
            cursor.execute(query)

    operations = [
        migrations.RunPython(add_history_columns),
    ]
