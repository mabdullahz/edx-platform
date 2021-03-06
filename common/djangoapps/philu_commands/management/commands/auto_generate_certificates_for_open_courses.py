"""
Django management command to auto generate certificates for all users
enrolled in currently running courses with early_no_info or early_with_info set
in the certificate_display_behavior setting in course advanced settings
"""
import json
from logging import getLogger

from django.core.management.base import BaseCommand

from courseware.views.views import _get_cert_data
from lms.djangoapps.certificates.models import CertificateStatuses
from lms.djangoapps.certificates.api import generate_user_certificates
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore

log = getLogger(__name__)

CERT_GENERATION_RESPONSE_MESSAGE = 'Certificate generation {} for user with ' \
                                   'username: {} and user_id: {} with ' \
                                   'generation status: {}'


def is_course_valid_for_certificate_auto_generation(course):
    return bool(course.has_started() and not course.has_ended() and course.may_certify())


class Command(BaseCommand):
    help = """
    The purpose of this command is to automatically generate certificates for
    all passed users (that do not have a certificate yet) in all currently
    running courses that have "certificate_display_behavior" set as
    "early_no_info" or "early_with_info"

    example:
        manage.py ... auto_generate_certificates_for_open_courses
    """

    def handle(self, *args, **options):
        for course in modulestore().get_courses():
            if not is_course_valid_for_certificate_auto_generation(course):
                continue

            for user_course_enrollment in CourseEnrollment.objects.filter(course=course.id, is_active=True).all():
                user = user_course_enrollment.user
                cert_data = _get_cert_data(user, course, user_course_enrollment.mode)

                if not cert_data or cert_data.cert_status != CertificateStatuses.requesting:
                    continue

                status = generate_user_certificates(user, course.id, course=course)

                if status:
                    log.info(CERT_GENERATION_RESPONSE_MESSAGE.format(
                        'passed', user.username, user.id, status))
                    # TODO: Send mail to user. Remove when story LP-1674 is completed

                else:
                    log.error(CERT_GENERATION_RESPONSE_MESSAGE.format(
                        'failed', user.username, user.id, status))
