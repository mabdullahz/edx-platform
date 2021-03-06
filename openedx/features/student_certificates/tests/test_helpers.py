"""
This file contains the test cases for helper functions of the student_certificates app
"""
import pytz

from xmodule.modulestore.tests.django_utils import SharedModuleStoreTestCase
from student.tests.factories import UserFactory
from student.models import CourseEnrollment
from xmodule.modulestore.tests.factories import CourseFactory
from certificates.tests.factories import GeneratedCertificateFactory
from openedx.features.student_certificates.helpers import (
    CERTIFICATE_IMG_PREFIX,
    get_philu_certificate_social_context,
    get_certificate_img_key,
    get_certificate_image_path,
    get_certificate_image_name,
    get_certificate_url,
    get_certificate_image_url,
)
from django.conf import settings


class GenerateStudentCertificateHelpersTestCase(SharedModuleStoreTestCase):
    """
        Tests for generating student course certificates.
    """

    @classmethod
    def setUpClass(cls):
        super(GenerateStudentCertificateHelpersTestCase, cls).setUpClass()
        cls.course = CourseFactory.create()

    def setUp(self):
        """ Setup components used by each certificate test."""
        super(GenerateStudentCertificateHelpersTestCase, self).setUp()
        self.download_url = 'http://www.example.com/certificate.pdf'
        self.user = UserFactory.create(username='jack', email='jack@fake.edx.org', password='test')
        self.enrollment = CourseEnrollment.enroll(self.user, self.course.id, mode='verified')
        self.certificate = GeneratedCertificateFactory(
            user=self.user,
            course_id=self.course.id,
            mode='honor',
            download_url=self.download_url,
            status="downloadable",
            grade=0.98,
        )

    def test_get_philu_certificate_social_context(self):
        """
            Test generation of social sharing urls for certificates
        """
        current_context = get_philu_certificate_social_context(self.course, self.certificate)
        certificate_uuid = self.certificate.verify_uuid
        
        self.assertTrue(certificate_uuid in current_context['twitter'])
        self.assertTrue(certificate_uuid in current_context['facebook'])
        self.assertTrue(certificate_uuid in current_context['email'])
        self.assertTrue(certificate_uuid in  current_context['linkedin'])
        self.assertTrue(certificate_uuid in current_context['facebook_after_enroll'])

    def test_get_certificate_img_url(self):
        """
            Test generation of certificate image url
        """
        expected_url = 'https://s3.amazonaws.com/{bucket}/{prefix}/{uuid}.jpg'.format(
            bucket=getattr(settings, "FILE_UPLOAD_STORAGE_BUCKET_NAME", None),
            prefix=CERTIFICATE_IMG_PREFIX,
            uuid=self.certificate.verify_uuid
        )
        current_url = get_certificate_image_url(self.certificate)

        self.assertEqual(expected_url, current_url)

    def test_get_certificate_url(self):
        """
            Test generation of certificate url
        """
        expected_url = '{root_url}/certificates/{uuid}?border=hide'.format(
            root_url=settings.LMS_ROOT_URL,
            uuid=self.certificate.verify_uuid
        )
        current_url = get_certificate_url(self.certificate.verify_uuid)

        self.assertEqual(expected_url, current_url)

    def test_get_certificate_image_name(self):
        """
            Test generation of certificate image name
        """
        expected_name = '{uuid}.jpg'.format(uuid=self.certificate.verify_uuid)
        current_name = get_certificate_image_name(self.certificate.verify_uuid)

        self.assertEqual(expected_name, current_name)

    def test_get_certificate_image_path(self):
        """
            Test generation of certificate image path
        """
        img_name = 'test.jpg'
        expected_path = '/tmp/{img}'.format(img=img_name)
        current_path = get_certificate_image_path(img_name)

        self.assertEqual(expected_path, current_path)

    def test_get_certificate_img_key(self):
        """
            Test generation of certificate image key
        """
        img_name = 'test.jpg'
        expected_img_key = '{prefix}/{img_name}'.format(prefix=CERTIFICATE_IMG_PREFIX, img_name=img_name)
        current_img_key = get_certificate_img_key(img_name)

        self.assertEqual(expected_img_key, current_img_key)
