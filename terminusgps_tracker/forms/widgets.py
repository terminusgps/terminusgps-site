from typing import Any
from datetime import date

from django import forms
from django.forms import widgets
from django.urls import reverse_lazy

from terminusgps_tracker.forms.choices import CountryCode


class TrackerTextInput(widgets.TextInput):
    input_type = "text"
    template_name = "terminusgps_tracker/forms/widgets/text.html"


class TrackerSelectInput(widgets.Select):
    template_name = "terminusgps_tracker/forms/widgets/select.html"

    def __init__(self, attrs=None, choices=None) -> None:
        if choices is None:
            choices = {}
        if attrs is None:
            attrs = {}
        super().__init__(attrs, choices)


class TrackerInput(widgets.Input):
    template_name = "terminusgps_tracker/forms/widgets/input.html"


class TrackerPasswordInput(widgets.Input):
    input_type = "password"
    template_name = "terminusgps_tracker/forms/widgets/password.html"


class TrackerDateInput(widgets.DateInput):
    input_type = "date"
    template_name = "terminusgps_tracker/forms/widgets/date.html"


class TrackerNumberInput(widgets.NumberInput):
    input_type = "number"
    template_name = "terminusgps_tracker/forms/widgets/number.html"


class TrackerEmailInput(widgets.EmailInput):
    input_type = "email"
    template_name = "terminusgps_tracker/forms/widgets/email.html"


class ExpirationDateWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/expiration_date.html"

    def __init__(self, attrs: dict | None = None) -> None:
        if attrs is None:
            attrs = {}

        month_attrs = attrs.copy()
        month_attrs.update({"placeholder": "MM"})
        year_attrs = attrs.copy()
        year_attrs.update({"placeholder": "YY"})
        widgets = {
            "month": TrackerTextInput(attrs=month_attrs),
            "year": TrackerTextInput(attrs=year_attrs),
        }
        super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value: date | str) -> list:
        if value:
            if isinstance(value, date):
                return [value.month, value.year]
            elif isinstance(value, str):
                month, year = value.split("/")
                return [month, year]
        return [None, None]

    def value_from_datadict(self, data, files, name: str) -> list[Any]:
        month, year = super().value_from_datadict(data, files, name)
        return [f"{month}/{year}"]


class CreditCardWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/credit_card.html"

    def __init__(self, attrs: dict | None = None) -> None:
        if attrs is None:
            attrs = {}
        base_attrs = attrs.copy()
        cc_number_attrs = base_attrs.copy()
        cc_number_attrs.update({"maxlength": "16", "placeholder": "123412341234"})
        cc_expiry_attrs = base_attrs.copy()
        cc_expiry_attrs.update({"maxlength": "2"})
        cc_ccv_attrs = base_attrs.copy()
        cc_ccv_attrs.update({"maxlength": "4", "placeholder": "123"})
        widgets = {
            "number": TrackerTextInput(attrs=cc_number_attrs),
            "expiry": ExpirationDateWidget(attrs=cc_expiry_attrs),
            "ccv": TrackerTextInput(attrs=cc_ccv_attrs),
        }

        return super().__init__(widgets=widgets, attrs=attrs)

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["number", "expiry_month", "expiry_year", "ccv"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)


class AddressWidget(forms.MultiWidget):
    template_name = "terminusgps_tracker/forms/widgets/address.html"

    def decompress(self, value: dict[str, Any]) -> list:
        data_keys = ["street", "city", "state", "zip", "country", "phone"]
        if value:
            return [value.get(key) for key in data_keys]
        return [None] * len(data_keys)

    def __init__(self, attrs: dict | None = None) -> None:
        if attrs is None:
            attrs = {}
        base_attrs = attrs.copy()
        street_attrs = base_attrs.copy()
        street_attrs.update(
            {
                "placeholder": "12345 Main St.",
                "hx-get": reverse_lazy("search address"),
                "hx-trigger": "keyup changed delay:500ms",
            }
        )
        city_attrs = base_attrs.copy()
        city_attrs.update(
            {
                "placeholder": "Houston",
                "hx-get": reverse_lazy("search address"),
                "hx-trigger": "keyup changed delay:500ms",
            }
        )
        state_attrs = base_attrs.copy()
        state_attrs.update(
            {
                "placeholder": "Texas",
                "hx-get": reverse_lazy("search address"),
                "hx-trigger": "keyup changed delay:500ms",
            }
        )
        zip_attrs = base_attrs.copy()
        zip_attrs.update(
            {
                "placeholder": "12345-1234",
                "hx-get": reverse_lazy("search address"),
                "hx-trigger": "keyup changed delay:500ms",
            }
        )
        country_attrs = base_attrs.copy()
        country_attrs.update(
            {
                "placeholder": "United States",
                "hx-get": reverse_lazy("search address"),
                "hx-trigger": "keyup changed delay:500ms",
            }
        )
        phone_attrs = base_attrs.copy()
        phone_attrs.update({"placeholder": "+12815555555"})
        widgets = {
            "street": TrackerTextInput(attrs=street_attrs),
            "city": TrackerTextInput(attrs=city_attrs),
            "state": TrackerTextInput(attrs=state_attrs),
            "zip": TrackerNumberInput(attrs=zip_attrs),
            "country": TrackerSelectInput(
                attrs=country_attrs, choices=CountryCode.choices
            ),
            "phone": TrackerTextInput(attrs=phone_attrs),
        }
        super().__init__(widgets=widgets, attrs=attrs)
