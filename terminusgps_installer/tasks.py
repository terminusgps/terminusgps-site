import logging

from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string
from django.utils import timezone

from terminusgps.wialon import get_resource, get_session, get_unit_by_imei

from .models import InstallJob

logger = logging.getLogger(__name__)


@task
def send_job_created_email(job_id: int) -> None:
    try:
        job = InstallJob.objects.get(pk=job_id)
    except InstallJob.DoesNotExist:
        logger.error(f"Failed to find job by id: {job_id}")
        return
    else:
        session = get_session(sid=None)
        unit = get_unit_by_imei(session, job.imei)
        resource = get_resource(session, job.resource)
        email_template_name = "installer/emails/job_created.txt"
        email_context = {
            "job_id": job.pk,
            "date": timezone.now(),
            "status": job.get_status_display(),
            "imei": job.imei,
            "vin": job.vin,
            "resource": resource["nm"],
            "unit": unit["nm"],
            "employee": str(job.employee),
        }
        email = EmailMultiAlternatives(
            subject=f"Job #{job_id} created",
            body=render_to_string(email_template_name, email_context),
            from_email="noreply@terminusgps.com",
            to=["pspeckman3@terminusgps.com"],
        )
        email.send(fail_silently=True)


@task
def send_job_updated_email(job_id: int) -> None:
    try:
        job = InstallJob.objects.get(pk=job_id)
    except InstallJob.DoesNotExist:
        logger.error(f"Failed to find job by id: {job_id}")
        return
    else:
        session = get_session(sid=None)
        unit = get_unit_by_imei(session, job.imei)
        resource = get_resource(session, job.resource)
        email_template_name = "installer/emails/job_updated.txt"
        email_context = {
            "job_id": job.pk,
            "date": timezone.now(),
            "status": job.status,
            "imei": job.imei,
            "vin": job.vin,
            "resource": resource["nm"],
            "unit": unit["nm"],
            "employee": str(job.employee),
        }
        email = EmailMultiAlternatives(
            subject=f"Job #{job_id} updated",
            body=render_to_string(email_template_name, email_context),
            from_email="noreply@terminusgps.com",
            to=["pspeckman3@terminusgps.com"],
        )
        email.send(fail_silently=True)
