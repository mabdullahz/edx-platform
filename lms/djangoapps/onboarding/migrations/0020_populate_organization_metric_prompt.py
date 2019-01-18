# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from lms.djangoapps.onboarding.helpers import its_been_year, its_been_year_month, \
    its_been_year_three_month, its_been_year_six_month
from mailchimp_pipeline.signals.handlers import sync_metric_update_prompt_with_mail_chimp


def get_latest_metric(org):
    """
    :param org:
    :return: latest organization metrics submitted by user
    """
    return org.organization_metrics.order_by('-submission_date')[0]


def get_latest_submission_date(org):
    """
    :param org:
    :return: latest date of latest metric submission
    """
    return get_latest_metric(org).submission_date


def get_responsible_user(org):
    """
    :param org:
    :return: return admin of organization if exists otherwise the person with latest
             metric submission is responsible user
    """
    return org.admin if org.admin else get_latest_metric(org).user


def metric_exists(org):
    """
    :param org:
    :return: True if some metrics exists against this organization, otherwise False
    """
    return bool(org.organization_metrics.all())


def create_org_metric_prompts(apps, schema_editor):

    Organization = apps.get_model("onboarding", "Organization")
    Prompt = apps.get_model("onboarding", "OrganizationMetricUpdatePrompt")
    organizations = Organization.objects.all()

    Prompt.objects.all().delete()
    for org in organizations:
        if metric_exists(org):
            prompt = Prompt()
            submission_date = get_latest_submission_date(org)

            prompt.org = org
            prompt.responsible_user = get_responsible_user(org)
            prompt.latest_metric_submission = submission_date
            prompt.year = its_been_year(submission_date)
            prompt.year_month = its_been_year_month(submission_date)
            prompt.year_three_month = its_been_year_three_month(submission_date)
            prompt.year_six_month = its_been_year_six_month(submission_date)
            prompt.save()
            sync_metric_update_prompt_with_mail_chimp(prompt)



class Migration(migrations.Migration):

    dependencies = [
        ('onboarding', '0019_organizationmetricupdateprompt'),
    ]

    operations = [
        migrations.RunPython(create_org_metric_prompts)
    ]
