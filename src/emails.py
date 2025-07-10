from urllib.parse import urlencode

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from terminusgps_tracker.models import Customer


def send_registration_email(customer: Customer) -> None:
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
        bcc=["pspeckman@terminusgps.com", "blake@terminusgps.com"],
    )
    msg.send(fail_silently=True)
