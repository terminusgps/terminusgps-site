from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from terminusgps_tracker.models import (
    CustomerPaymentMethod,
    CustomerShippingAddress,
)


class SubscriptionCreationForm(forms.Form):
    payment = forms.ModelChoiceField(
        empty_label=mark_safe("<p>Retrieving...</p>"),
        label="Payment Method",
        queryset=CustomerPaymentMethod.objects.none(),
        widget=forms.widgets.Select(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "hx-target": "this",
                "hx-trigger": "load",
            }
        ),
    )
    address = forms.ModelChoiceField(
        empty_label=mark_safe("<p>Retrieving...</p>"),
        label="Shipping Address",
        queryset=CustomerShippingAddress.objects.none(),
        widget=forms.widgets.Select(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "hx-target": "this",
                "hx-trigger": "load",
            }
        ),
    )
    coupon_code = forms.CharField(
        max_length=24,
        label="Coupon Code",
        help_text="Optionally enter a coupon code for your new subscription.",
        required=False,
        widget=forms.widgets.TextInput(
            attrs={
                "class": settings.DEFAULT_FIELD_CLASS,
                "placeholder": "12345678",
            }
        ),
    )
