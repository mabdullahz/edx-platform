"""
The urls for On Demand Email Preferences app.
"""

from django.conf.urls import url
from django.conf import settings
from openedx.features.ondemand_email_preferences import views

urlpatterns = [
    url(r"^update_email_preferences_component/{}/?$".format(settings.COURSE_ID_PATTERN),
        views.update_on_demand_emails_preferences_component, name="update_email_preferences_component")
]
