from django import forms

from terminusgps_tracker.models import CustomerSubscription, SubscriptionTier


class CustomerSubscriptionUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomerSubscription
        fields = ["address", "payment", "tier"]
        widgets = {
            "tier": forms.widgets.Select(
                choices=SubscriptionTier.objects.all(),
                attrs={
                    "class": "p-2 w-full bg-stone-100 dark:bg-gray-700 dark:text-white rounded border",
                    "required": True,
                },
            ),
            "address": forms.widgets.HiddenInput(),
            "payment": forms.widgets.HiddenInput(),
        }
