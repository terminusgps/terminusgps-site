from typing import Any, Collection, Sequence

from django import forms
from django.db.models import TextChoices

from terminusgps_tracker.forms.choices import CountryChoice
from terminusgps_tracker.forms.widgets import TrackerSelectInput, TrackerTextInput
from terminusgps_tracker.forms.multiwidgets import CountryStateWidget


class CountryStateField(forms.MultiValueField):
    def __init__(self, **kwargs) -> None:
        fields = (forms.ChoiceField(), forms.ChoiceField())
        widget = CountryStateWidget(
            widgets={"state": TrackerSelectInput(), "country": TrackerSelectInput()}
        )
        return super().__init__(fields=fields, widget=widget, **kwargs)


class CreditCardField(forms.MultiValueField):
    def __init__(
        self,
        fields: Sequence[forms.Field],
        widget: forms.widgets.MultiWidget | None = None,
        **kwargs,
    ) -> None:
        self.field_keys = ["number", "expiry_month", "expiry_year", "ccv"]
        self.require_all_fields = True
        super().__init__(fields=fields, widget=widget, **kwargs)

    def compress(self, data_list: Collection) -> dict[str, Any]:
        if data_list:
            return dict(zip(self.field_keys, data_list))
        return dict(zip(self.field_keys, [None] * len(self.field_keys)))


class AddressField(forms.MultiValueField):
    def __init__(
        self, fields: Sequence[forms.Field], widget: forms.widgets.MultiWidget, **kwargs
    ) -> None:
        self.field_keys: list[str] = [
            "street",
            "city",
            "state",
            "zip",
            "country",
            "phone",
        ]
        self.require_all_fields: bool = False
        return super().__init__(fields=fields, widget=widget, **kwargs)

    def compress(self, data_list: Collection) -> dict[str, Any]:
        if data_list:
            return dict(zip(self.field_keys, data_list))
        return dict(zip(self.field_keys, [None] * len(self.field_keys)))
