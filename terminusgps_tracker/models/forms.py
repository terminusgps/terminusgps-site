from django import forms
from django.urls import reverse


class RegistrationForm(forms.Form):
    name = "registration"
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
    )
    email = forms.EmailField(
        required=True,
        label="Email",
    )
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        label="Phone #",
    )
    asset_name = forms.CharField(
        max_length=255,
        required=True,
        label="Asset Name",
    )
    imei_number = forms.CharField(
        max_length=20,
        required=True,
        disabled=True,
        label="IMEI #",
    )

    def get_absolute_url(self):
        return reverse("registration-detail", kwargs={"id": self.id})


class PersonForm(forms.Form):
    name = "person"
    fn = forms.CharField(label="First Name", max_length=64)
    ln = forms.CharField(label="Last Name", max_length=64)
