from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models.subscriptions import CustomerSubscription


class CustomerSubscriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerSubscription
        fields = ["address", "payment", "tier"]
        widgets = {
            "tier": forms.widgets.Select(
                choices=[(1, _("Basic")), (2, _("Standard")), (3, _("Premium"))],
                attrs={"class": settings.DEFAULT_FIELD_CLASS, "required": True},
            ),
            "address": forms.widgets.HiddenInput(),
            "payment": forms.widgets.HiddenInput(),
        }
