from django import forms
from django.conf import settings

from terminusgps_tracker.models import (
    CustomerPaymentMethod,
    CustomerShippingAddress,
)


class SubscriptionCreationForm(forms.Form):
    payment = forms.ModelChoiceField(
        empty_label=None,
        label="Payment Method",
        queryset=CustomerPaymentMethod.objects.none(),
        widget=forms.widgets.Select(
            attrs={"class": settings.DEFAULT_FIELD_CLASS}
        ),
    )
    address = forms.ModelChoiceField(
        empty_label=None,
        label="Shipping Address",
        queryset=CustomerShippingAddress.objects.none(),
        widget=forms.widgets.Select(
            attrs={"class": settings.DEFAULT_FIELD_CLASS}
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
