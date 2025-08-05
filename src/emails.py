from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from terminusgps_tracker.models import Customer


def get_admin_email_list() -> list[str]:
    return [admin[1] for admin in settings.ADMINS]


def send_registration_email(customer: Customer) -> Customer:
    context = {
        "first_name": customer.user.first_name,
        "login_link": f"https://app.terminusgps.com/login?{urlencode({'username': customer.user.email})}",
    }
    text_content = render_to_string(
        "terminusgps/emails/registration_complete.txt", context=context
    )
    msg = EmailMultiAlternatives(
        subject="Terminus GPS - Account Registered",
        body=text_content,
        to=[customer.user.email],
        bcc=get_admin_email_list(),
    )
    msg.send(fail_silently=True)

    return customer
