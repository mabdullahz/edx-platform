"""
The urls for philu features app.
"""
from django.conf.urls import url

from openedx.features.student_certificates import views

urlpatterns = [
    url(r"^certificates/$", views.student_certificates, name="certificates"),
    url(r"^shared_certificates/(?P<certificate_uuid>[0-9a-f]{32})$", views.shared_student_certificate,
        name="shared_certificate"),
]
