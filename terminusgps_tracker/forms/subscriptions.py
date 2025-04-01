from django import forms
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models.subscriptions import CustomerSubscription


class CustomerSubscriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerSubscription
        fields = ["address", "payment", "tier"]
        widgets = {
            "tier": forms.widgets.Select(
                choices=[(1, _("Basic")), (2, _("Standard")), (3, _("Premium"))],
                attrs={
                    "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border",
                    "required": True,
                },
            ),
            "address": forms.widgets.HiddenInput(),
            "payment": forms.widgets.HiddenInput(),
        }
