from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

from terminusgps_tracker.models import (
    CustomerPaymentMethod,
    CustomerShippingAddress,
    SubscriptionFeature,
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
    features = forms.ModelChoiceField(
        label="Additonal Features",
        help_text="Ctrl+click to select multiple, Cmd+click on Mac",
        queryset=SubscriptionFeature.objects.all(),
        empty_label=None,
        required=False,
        widget=forms.widgets.SelectMultiple(
            attrs={"class": settings.DEFAULT_FIELD_CLASS}
        ),
    )
