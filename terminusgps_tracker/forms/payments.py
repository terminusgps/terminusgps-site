from django import forms
from django.utils.translation import gettext_lazy as _

COUNTRY_CHOICES = {
    ("BR", _("Brazil")),
    ("BS", _("The Bahamas")),
    ("CA", _("Canada")),
    ("MX", _("Mexico")),
    ("UM", _("United States Minor Outlying Islands")),
    ("VI", _("United States Virgin Islands")),
    ("ST", _("São Tomé and Príncipe")),
    ("VI", _("United States Virgin Islands")),
    ("US", _("United States")),
}


class PaymentMethodUploadForm(forms.Form):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")
    address_street = forms.CharField(label="Street")
    address_city = forms.CharField(label="City")
    address_state = forms.CharField(label="State")
    address_zip = forms.CharField(label="Zip")
    address_country = forms.ChoiceField(label="Country", choices=COUNTRY_CHOICES)
    card_number = forms.CharField(label="Card Number")
    card_expiration_date = forms.DateField(input_formats=["%m/%d"])
    card_security_code = forms.CharField(label="CCV")
