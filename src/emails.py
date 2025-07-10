from urllib.parse import urlencode

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from terminusgps_tracker.models import Customer


def send_registration_email(customer: Customer) -> Customer:
    text_content = render_to_string(
        "terminusgps/emails/registration_complete.txt",
        context={
            "first_name": customer.user.first_name,
            "login_link": f"https://app.terminusgps.com/login?{urlencode({'username': customer.user.email})}",
        },
    )
    msg = EmailMultiAlternatives(
        subject="Terminus GPS - Account Registered",
        body=text_content,
        from_email="support@terminusgps.com",
        to=[customer.user.email],
        bcc=["pspeckman@terminusgps.com", "blake@terminusgps.com"],
    )
    msg.send(fail_silently=True)
    return customer
