from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string
from django.utils import timezone

from .models import InstallJob


@task
def send_job_status_updated_email(job_id: int, old_status: str) -> int:
    job = InstallJob.objects.get(pk=job_id)
    context = {
        "old_status": old_status,
        "new_status": job.status,
        "date": timezone.now(),
    }
    text_content = render_to_string(
        "installer/emails/job_status_updated.txt", context=context
    )
    html_content = render_to_string(
        "installer/emails/job_status_updated.html", context=context
    )
    msg = EmailMultiAlternatives(
        subject=f"Job #{job_id} Status Updated",
        body=text_content,
        from_email="noreply@terminusgps.com",
        to=["support@terminusgps.com"],
        bcc=["peter@terminusgps.com", "blake@terminusgps.com"],
    )
    msg.attach_alternative(html_content, "text/html")
    return msg.send(fail_silently=True)
