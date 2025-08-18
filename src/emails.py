from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from terminusgps_tracker.models import Customer


def send_registration_email(customer: Customer) -> None:
    email_content = render_to_string(
        "terminusgps/emails/registration_complete.txt",
        context={
            "first_name": customer.user.first_name,
            "login_link": f"https://app.terminusgps.com/login?{urlencode({'username': customer.user.email})}",
        },
    )
    EmailMultiAlternatives(
        subject="Terminus GPS - Account Registered",
        body=email_content,
        to=[customer.user.email],
        bcc=[admin[1] for admin in settings.ADMINS],
    ).send(fail_silently=True)
