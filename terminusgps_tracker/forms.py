from django import forms
from terminusgps_payments.models import AddressProfile, PaymentProfile


class SubscriptionCreationForm(forms.Form):
    payment_profile = forms.ModelChoiceField(
        queryset=PaymentProfile.objects.none(),
        empty_label=None,
        widget=forms.widgets.Select(
            attrs={"class": "p-2 rounded border bg-gray-100"}
        ),
    )
    address_profile = forms.ModelChoiceField(
        queryset=AddressProfile.objects.none(),
        empty_label=None,
        widget=forms.widgets.Select(
            attrs={"class": "p-2 rounded border bg-gray-100"}
        ),
    )
    consent = forms.BooleanField(
        initial=False,
        widget=forms.widgets.CheckboxInput(
            attrs={"class": "accent-terminus-red-700"}
        ),
    )
