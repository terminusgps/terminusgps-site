from django import forms
from django.conf import settings

from terminusgps_tracker.models.subscriptions import Subscription


class SubscriptionCreationForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["address", "payment", "tier"]
        widgets = {
            "tier": forms.widgets.Select(
                attrs={"class": settings.DEFAULT_FIELD_CLASS}
            ),
            "address": forms.widgets.Select(
                attrs={"class": settings.DEFAULT_FIELD_CLASS}
            ),
            "payment": forms.widgets.Select(
                attrs={"class": settings.DEFAULT_FIELD_CLASS}
            ),
        }
