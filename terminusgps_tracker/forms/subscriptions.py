from django import forms
from django.conf import settings

from terminusgps_tracker.models import (
    CustomerPaymentMethod,
    CustomerShippingAddress,
)


class CustomerSubscriptionCreationForm(forms.Form):
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


class CustomerSubscriptionUpdateForm(forms.Form):
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
