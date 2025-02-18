from typing import Any
from django import forms
from django.forms import ValidationError, widgets
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models import TrackerSubscription


class SubscriptionBaseForm(forms.ModelForm):
    class Meta:
        model = TrackerSubscription
        fields = ("tier", "payment_id", "address_id")
        widgets = {
            "tier": widgets.Select(
                choices=((_("Basic"), 1), (_("Standard"), 2), (_("Premium"), 3)),
                attrs={
                    "class": "w-full block p-4 text-lg dark:bg-gray-600 dark:text-gray-100 bg-white border border-gray-600 rounded"
                },
            ),
            "payment_id": widgets.HiddenInput(),
            "address_id": widgets.HiddenInput(),
        }

    def clean(self) -> dict[str, Any] | None:
        cleaned_data: dict[str, Any] | None = super().clean()
        if cleaned_data:
            payment_id = cleaned_data.get("payment_id")
            address_id = cleaned_data.get("address_id")
            if not payment_id and not address_id:
                raise ValidationError(
                    _(
                        "Whoops! Both 'payment_id' and 'address_id' must be provided, got '%(payment_id)s' and '%(address_id)s'"
                    ),
                    code="invalid",
                    params={"payment_id": payment_id, "address_id": address_id},
                )
        return cleaned_data


class SubscriptionCancelForm(SubscriptionBaseForm):
    """Cancel form."""


class SubscriptionUpdateForm(SubscriptionBaseForm):
    """Update form."""
