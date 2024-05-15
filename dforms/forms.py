from django import forms

from dforms.integrations.wialon.validators import validate_wialon_imei


class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=24)
    last_name = forms.CharField(max_length=24)
    email = forms.EmailField()
    imei = forms.CharField(max_length=24, validators=[validate_wialon_imei])
    asset_name = forms.CharField(max_length=256)
    phone = forms.CharField(max_length=15)
    vin = forms.CharField(max_length=17)


class NewsletterSignupForm(forms.Form):
    email = forms.EmailField()
    opted_in = forms.BooleanField(required=True)
