from collections.abc import Sequence

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.tasks import task
from django.template.loader import render_to_string


@task
def send_email(
    subject: str,
    to: Sequence[str],
    template_name: str,
    context: dict | None = None,
    from_email: str = settings.DEFAULT_FROM_EMAIL,
    reply_to: str = settings.DEFAULT_REPLY_TO_EMAIL,
    html_template_name: str | None = None,
    headers: dict | None = None,
):
    email = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string(template_name=template_name, context=context),
        to=to,
        from_email=from_email,
        headers=headers if headers is not None else {},
        bcc=[admin[1] for admin in settings.ADMINS],
    )

    if html_template_name is not None:
        email.attach_alternative(
            render_to_string(
                template_name=html_template_name, context=context
            ),
            "text/html",
        )
    email.send(fail_silently=True)
