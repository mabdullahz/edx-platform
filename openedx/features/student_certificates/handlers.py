from django.db.models.signals import post_save
from django.dispatch import receiver

from lms.djangoapps.certificates.models import GeneratedCertificate

from models import CertificateVerificationKey
from tasks import task_create_certificate_img_and_upload_to_s3


@receiver(post_save, sender=GeneratedCertificate)
def generate_certificate_img(instance, created, **kwargs):
    if not created:
        task_create_certificate_img_and_upload_to_s3.delay(instance.verify_uuid)


@receiver(post_save, sender=GeneratedCertificate)
def generate_certificate_verification_key(instance, created, **kwargs):
    if created and not hasattr(instance, 'certificate_verification_key'):
        CertificateVerificationKey.objects.create_object(instance)
