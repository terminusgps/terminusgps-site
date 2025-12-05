from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from terminusgps_payments.forms import (
    AddressProfileChoiceField,
    PaymentProfileChoiceField,
)
from terminusgps_payments.models import AddressProfile, PaymentProfile

WIDGET_CSS_CLASS = (
    settings.WIDGET_CSS_CLASS
    if hasattr(settings, "WIDGET_CSS_CLASS")
    else "peer p-2 rounded border border-current bg-gray-50 dark:bg-gray-600 user-invalid:bg-red-50 user-invalid:text-red-600"
)


class SubscriptionCreateForm(forms.Form):
    payment_profile = PaymentProfileChoiceField(
        queryset=PaymentProfile.objects.none(),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=mark_safe(
            "Select a payment profile from the list. Click <a href='/account/' class='w-fit decoration text-terminus-red-200 underline decoration-terminus-black underline-offset-4 hover:text-terminus-red-100 hover:decoration-dotted dark:decoration-white'>here</a> to add one."
        ),
    )
    address_profile = AddressProfileChoiceField(
        queryset=AddressProfile.objects.none(),
        widget=forms.widgets.Select(attrs={"class": WIDGET_CSS_CLASS}),
        help_text=mark_safe(
            "Select an address profile from the list. Click <a href='/account/' class='w-fit decoration text-terminus-red-200 underline decoration-terminus-black underline-offset-4 hover:text-terminus-red-100 hover:decoration-dotted dark:decoration-white'>here</a> to add one."
        ),
    )
