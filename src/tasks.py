from datetime import datetime
from urllib.parse import urljoin

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django_tasks import task


@task
def send_account_created_email(
    email_address: str,
    first_name: str | None = None,
    create_date: datetime | None = None,
) -> None:
    context = {
        "first_name": first_name,
        "create_date": create_date,
        "dashboard_link": urljoin(
            "https://app.terminusgps.com/", reverse("dashboard")
        ),
    }
    text_content = render_to_string(
        "terminusgps/emails/account_created.txt", context=context
    )
    html_content = render_to_string(
        "terminusgps/emails/account_created.html", context=context
    )
    msg = EmailMultiAlternatives(
        subject="Terminus GPS - Account Created",
        body=text_content,
        to=[email_address],
        bcc=[admin[1] for admin in settings.ADMINS],
    )
    msg.attach_alternative(html_content, "text/html")
    return bool(msg.send(fail_silently=True))
