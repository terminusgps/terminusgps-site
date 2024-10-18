from django import forms
from django.forms.renderers import TemplatesSetting
from django.http import HttpRequest, HttpResponse

from terminusgps_tracker.forms.fields import AddressField, CreditCardField
from terminusgps_tracker.forms.validators import (
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_user_name,
)


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/forms/partials/_form.html"
    field_template_name = "terminusgps_tracker/forms/partials/_field.html"
    formset_template_name = "terminusgps_tracker/forms/partials/_formset.html"

    def get_template(self, template_name: str, **kwargs):
        if template_name.startswith("django/forms/widgets/"):
            template_name = template_name.replace(
                "django/forms/widgets/", "terminusgps_tracker/forms/partials/_"
            )
        elif template_name.startswith("django/forms/"):
            template_name = template_name.replace(
                "django/forms/", "terminusgps_tracker/forms/"
            )
        return super().get_template(template_name, **kwargs)


class CustomerRegistrationForm(forms.Form):
    first_name = forms.CharField(label="First Name", max_length=64)
    last_name = forms.CharField(label="Last Name", max_length=64)
    email = forms.EmailField(
        label="Email Address", validators=[validate_wialon_user_name], max_length=512
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.widgets.PasswordInput(),
        validators=[validate_wialon_password],
        min_length=4,
        max_length=32,
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.widgets.PasswordInput(),
        validators=[validate_wialon_password],
        min_length=4,
        max_length=32,
    )


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(label="Email Address")
    password = forms.CharField(label="Password", widget=forms.widgets.PasswordInput())


class AssetCustomizationForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name", validators=[validate_wialon_unit_name]
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=forms.widgets.NumberInput(),
    )


class CreditCardUploadForm(forms.Form):
    credit_card = CreditCardField(label="Credit Card")
    address = AddressField(label="Billing Address")
