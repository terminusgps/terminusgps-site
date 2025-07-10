import datetime

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from terminusgps_tracker.models import Customer


def send_subscription_created_email(
    customer: Customer, date: datetime.datetime
) -> None:
    context = {"first_name": customer.user.first_name, "create_date": date}
    text_content = render_to_string(
        "terminusgps/emails/subscription_created.txt", context=context
    )
    msg = EmailMultiAlternatives(
        subject="Terminus GPS - Subscription Created",
        body=text_content,
        to=[customer.user.email],
        bcc=["pspeckman@terminusgps.com", "blake@terminusgps.com"],
    )
    msg.send(fail_silently=True)


def send_subscription_canceled_email(
    customer: Customer, date: datetime.datetime
) -> None:
    context = {
        "first_name": customer.user.first_name,
        "cancel_date": date,
        "remaining_days": customer.subscription.get_remaining_days(),
    }
    text_content = render_to_string(
        "terminusgps/emails/subscription_canceled.txt", context=context
    )
    msg = EmailMultiAlternatives(
        subject="Terminus GPS - Subscription Canceled",
        body=text_content,
        to=[customer.user.email],
        bcc=["pspeckman@terminusgps.com", "blake@terminusgps.com"],
    )
    msg.send(fail_silently=True)
