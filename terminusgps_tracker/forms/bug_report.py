from django import forms
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class BugReportForm(forms.Form):
    class BugCategory(models.TextChoices):
        ASSET = "AS", _("Assets")
        PAYMENT_METHOD = "PM", _("Payment Methods")
        SHIPPING_ADDRESS = "SA", _("Shipping Addresses")
        SUBSCRIPTION = "SB", _("Subscriptions")
        OTHER = "OT", _("Other")

    text = forms.CharField(
        max_length=2048,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "I clicked the 'Delete' button on a payment method and it didn't do anything...",
                "class": "p-2 rounded bg-white text-gray-800",
                "rows": 10,
                "wrap": "soft",
            }
        ),
    )
    category = forms.ChoiceField(
        choices=BugCategory.choices,
        widget=forms.widgets.Select(
            attrs={"class": "p-2 rounded bg-white text-gray-800"}
        ),
    )
    user = forms.ModelChoiceField(queryset=get_user_model().objects.filter())
