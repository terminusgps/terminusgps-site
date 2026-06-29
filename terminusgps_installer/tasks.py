import logging

from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string

from terminusgps.wialon import get_resource, get_session, get_unit_by_imei

from .models import InstallJob

logger = logging.getLogger(__name__)


@task
def send_job_created_email(pk: int) -> None:
    try:
        job = InstallJob.objects.get(pk=pk)
    except InstallJob.DoesNotExist:
        logger.error(f"Failed to find job by id: {pk}")
        return
    else:
        session = get_session(sid=None)
        unit = get_unit_by_imei(session, job.imei)
        resource = get_resource(session, job.resource)
        email_template_name = "installer/emails/job_created.txt"
        email_context = {
            "job": job,
            "resource": resource["nm"],
            "unit": unit["nm"],
        }
        email = EmailMultiAlternatives(
            subject=f"Job #{pk} created",
            body=render_to_string(email_template_name, email_context),
            to=["pspeckman3@terminusgps.com"],
            cc=["support@terminusgps.com"],
        )
        email.send()


@task
def send_job_updated_email(pk: int) -> None:
    try:
        job = InstallJob.objects.get(pk=pk)
    except InstallJob.DoesNotExist:
        logger.error(f"Failed to find job by id: {pk}")
        return
    else:
        session = get_session(sid=None)
        unit = get_unit_by_imei(session, job.imei)
        resource = get_resource(session, job.resource)
        email_template_name = "installer/emails/job_updated.txt"
        email_context = {
            "job": job,
            "resource": resource["nm"],
            "unit": unit["nm"],
        }
        email = EmailMultiAlternatives(
            subject=f"Job #{pk} updated",
            body=render_to_string(email_template_name, email_context),
            to=["pspeckman3@terminusgps.com"],
            cc=["support@terminusgps.com"],
        )
        email.send()
