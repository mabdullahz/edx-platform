from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from edxmako.shortcuts import render_to_response
from lms.djangoapps.philu_api.helpers import get_course_custom_settings, get_social_sharing_urls

from certificates import api as certs_api
from lms.djangoapps.grades.models import PersistentCourseGrade
from courseware.courses import get_course
from certificates.models import (
    GeneratedCertificate,
    CertificateStatuses)
from common.djangoapps.student.views import get_course_enrollments


@login_required
@ensure_csrf_cookie
def student_certificates(request):
    """
    Provides the User with all certificates generated for the user

    Arguments:
        request: The request object.

    Returns:
        The generated certifcates list response.

    """
    user = request.user

    # we want to filter and only show enrollments for courses within
    # the 'ORG' defined in configuration.
    course_org_filter = configuration_helpers.get_value('course_org_filter')

    # Let's filter out any courses in an "org" that has been declared to be
    # in a configuration
    org_filter_out_set = configuration_helpers.get_all_orgs()

    # remove our current org from the "filter out" list, if applicable
    if course_org_filter:
        org_filter_out_set.remove(course_org_filter)

    # Build our (course, enrollment) list for the user, but ignore any courses that no
    # longer exist (because the course IDs have changed). Still, we don't delete those
    # enrollments, because it could have been a data push snafu.
    course_enrollments = list(get_course_enrollments(user, course_org_filter, org_filter_out_set))

    # sort the enrollment pairs by the enrollment date
    course_enrollments.sort(key=lambda x: x.created, reverse=True)

    # Retrieve the course modes for each course
    enrolled_course_ids = [enrollment.course_id for enrollment in course_enrollments]

    user_certificates = []

    available_certificates = GeneratedCertificate.objects.filter(user=user, course_id__in=enrolled_course_ids).all()

    for certificate in available_certificates:
        certificate_url = None
        course_id = certificate.course_id
        course = get_course(course_id)
        cert_downloadable_status = certs_api.certificate_downloadable_status(user, course_id)

        if cert_downloadable_status['is_downloadable']:
            certificate_url = cert_downloadable_status['download_url']

            if certs_api.has_html_certificates_enabled(course_id, course):
                if certs_api.get_active_web_certificate(course) is not None:
                    certificate_url = certs_api.get_certificate_url(
                        course_id=course_id, uuid=cert_downloadable_status['uuid']
                    )
                else:
                    continue

        if not certificate_url:
            continue

        course_name = course.display_name

        start_date = course.start

        try:
            completion_date = course.end
        except Exception as ex:
            completion_date = datetime.now()

        try:
            course_title = course.certificates['certificates'].pop()['course_title']
        except IndexError as ex:
            course_title = course.display_name
        except TypeError as ex:
            course_title = course.display_name

        custom_settings = get_course_custom_settings(course_id)
        meta_tags = custom_settings.get_course_meta_tags()

        # meta_tags['description'] = meta_tags['description'] or course_details.short_description
        # meta_tags['title'] = meta_tags['title'] or course_details.title or course.display_name
        meta_tags['title'] = meta_tags['title'] or 'I just completed Philanthropy University\'s ' \
                             + course.display_name + ' course! '

        # if course_details.banner_image_name != DEFAULT_IMAGE_NAME:
        #     meta_tags['image'] = settings.LMS_ROOT_URL + course_details.banner_image_asset_path

        # social_sharing_urls = get_social_sharing_urls(settings.LMS_ROOT_URL + certificate_url, meta_tags)
        social_sharing_urls = get_social_sharing_urls(
            settings.LMS_ROOT_URL + "/shared_certificates/" + certificate.verify_uuid, meta_tags)

        user_certificates.append({
            'course_name': course_name,
            'course_title': course_title,
            'social_sharing_urls': social_sharing_urls,
            'certificate_url': "%s%s" % (settings.LMS_ROOT_URL, certificate_url),
            'course_start': start_date.strftime('%b %d, %Y') if start_date else None,
            'completion_date': completion_date.strftime('%b %d, %Y') if completion_date else None,
        })

    context = {
        'user_certificates': user_certificates
    }

    response = render_to_response('certificates.html', context)
    return response


@login_required
@ensure_csrf_cookie
def shared_student_certificate(request, certificate_uuid):
    """
    Provides the User with the shared certificate page

    Arguments:
        request: The request object.

    Returns:
        The generated shared certificate response.

    """
    user = request.user

    try:
        certificate = GeneratedCertificate.eligible_certificates.get(
            verify_uuid=certificate_uuid,
            status=CertificateStatuses.downloadable
        )
    except GeneratedCertificate.DoesNotExist:
        raise Http404

    context = {
        'course_url': "%s%s%s%s" % (settings.LMS_ROOT_URL, '/courses/', certificate.course_id, '/about'),
    }

    response = render_to_response('shared_certificate.html', context)
    return response
