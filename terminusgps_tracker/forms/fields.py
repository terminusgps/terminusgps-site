from authorizenet import apicontractsv1
from django import forms
from django.utils import timezone
from terminusgps.django.validators import validate_e164_phone_number

from terminusgps_tracker.validators import validate_credit_card_number


class AddressWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_tracker/widgets/address.html"

    def __init__(self, attrs=None, field_attrs=None) -> None:
        if attrs is None:
            attrs = {}
        if field_attrs is None:
            field_attrs = [{} for _ in range(8)]
        widgets = {
            "first_name": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "First Name"} | field_attrs[0]
            ),
            "last_name": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "Last Name"} | field_attrs[1]
            ),
            "phone_number": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "+17139045262"} | field_attrs[2]
            ),
            "street": forms.widgets.TextInput(
                attrs=attrs
                | {"placeholder": "17610 South Dr"}
                | field_attrs[3]
            ),
            "city": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "Cypress"} | field_attrs[4]
            ),
            "state": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "Texas"} | field_attrs[5]
            ),
            "zip": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "77433"} | field_attrs[6]
            ),
            "country": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "USA"} | field_attrs[7]
            ),
        }
        super().__init__(widgets, attrs)

    def decompress(self, value) -> list[str | None]:
        if value:
            return [
                value.firstName,
                value.lastName,
                value.phoneNumber,
                value.address,
                value.city,
                value.state,
                value.zip,
                value.country,
            ]
        return [None, None, None, None, None, None, None, None]


class AddressField(forms.MultiValueField):
    @staticmethod
    def get_field_attrs(fields: tuple) -> list[dict[str, str]]:
        field_attrs = []
        for field in fields:
            attrs = {}
            if hasattr(field, "min_length") and field.min_length:
                attrs["minlength"] = field.min_length
            if hasattr(field, "max_length") and field.max_length:
                attrs["maxlength"] = field.max_length
            field_attrs.append(attrs)
        return field_attrs

    def __init__(self, **kwargs) -> None:
        error_messages = {}
        fields = (
            forms.CharField(label="First Name", min_length=4, max_length=16),
            forms.CharField(label="Last Name", min_length=4, max_length=16),
            forms.CharField(
                label="Phone #", validators=[validate_e164_phone_number]
            ),
            forms.CharField(label="Street", min_length=4, max_length=64),
            forms.CharField(label="City", min_length=4, max_length=64),
            forms.CharField(label="State", min_length=4, max_length=64),
            forms.CharField(label="Zip #", min_length=5, max_length=10),
            forms.CharField(label="Country", min_length=2, max_length=16),
        )
        widget = AddressWidget(
            attrs={
                "class": "p-2 rounded border border-current w-full text-gray-800 bg-gray-50 dark:text-gray-100 dark:bg-gray-400 group-has-[.errorlist]:text-red-600 group-has-[.errorlist]:bg-red-100"
            },
            field_attrs=self.get_field_attrs(fields),
        )
        super().__init__(
            error_messages=error_messages,
            fields=fields,
            widget=widget,
            require_all_fields=True,
            **kwargs,
        )

    def compress(self, data_list) -> apicontractsv1.customerAddressType:
        return apicontractsv1.customerAddressType(
            firstName=data_list[0],
            lastName=data_list[1],
            phoneNumber=data_list[2],
            address=data_list[3],
            city=data_list[4],
            state=data_list[5],
            zip=data_list[6],
            country=data_list[7],
        )


class CreditCardWidget(forms.widgets.MultiWidget):
    template_name = "terminusgps_tracker/widgets/credit_card.html"

    def __init__(self, attrs=None, field_attrs=None) -> None:
        if attrs is None:
            attrs = {}
        if field_attrs is None:
            field_attrs = [{} for _ in range(3)]
        now = timezone.now()
        widgets = {
            "number": forms.widgets.TextInput(
                attrs=attrs
                | {"placeholder": "4111111111111111"}
                | field_attrs[0]
            ),
            "expiry_month": forms.widgets.TextInput(
                attrs=attrs
                | {"placeholder": now.strftime("%m"), "maxlength": "2"}
                | field_attrs[1]
            ),
            "expiry_year": forms.widgets.TextInput(
                attrs=attrs
                | {"placeholder": now.strftime("%y"), "maxlength": "2"}
                | field_attrs[2]
            ),
            "ccv": forms.widgets.TextInput(
                attrs=attrs | {"placeholder": "444"} | field_attrs[3]
            ),
        }
        super().__init__(widgets, attrs)

    def decompress(self, value) -> list[str | None]:
        if value:
            return [value.cardNumber, value.expirationDate, value.cardCode]
        return [None, None, None]


class CreditCardField(forms.MultiValueField):
    @staticmethod
    def get_field_attrs(fields: tuple) -> list[dict[str, str]]:
        field_attrs = []
        for field in fields:
            attrs = {}
            if hasattr(field, "min_length") and field.min_length:
                attrs["minlength"] = field.min_length
            if hasattr(field, "max_length") and field.max_length:
                attrs["maxlength"] = field.max_length
            field_attrs.append(attrs)
        return field_attrs

    def __init__(self, **kwargs) -> None:
        error_messages = {}
        fields = (
            forms.CharField(
                label="Card #",
                min_length=16,
                validators=[validate_credit_card_number],
            ),
            forms.IntegerField(
                label="Expiry Month", min_value=1, max_value=12
            ),
            forms.IntegerField(
                label="Expiry Year",
                min_value=int(str(timezone.now().year)[-2:]),
                max_value=99,
            ),
            forms.CharField(label="CCV #"),
        )
        widget = CreditCardWidget(
            attrs={
                "class": "p-2 rounded border border-current w-full text-gray-800 bg-gray-50 dark:text-gray-100 dark:bg-gray-400 group-has-[.errorlist]:text-red-600 group-has-[.errorlist]:bg-red-100"
            },
            field_attrs=self.get_field_attrs(fields),
        )
        super().__init__(
            error_messages=error_messages,
            fields=fields,
            widget=widget,
            require_all_fields=True,
            **kwargs,
        )

    def compress(self, data_list) -> apicontractsv1.creditCardType:
        return apicontractsv1.creditCardType(
            cardNumber=data_list[0],
            expirationDate=f"{data_list[2] + 2000}-{data_list[1]:02}",
            cardCode=data_list[3],
        )
