from django import forms


class RegistrationForm(forms.Form):
    name = "register"
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


class PersonForm(forms.Form):
    name = "person"
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


class ContactForm(forms.Form):
    name = "contact"
    email = forms.EmailField(
        required=True,
        label="Email",
    )
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        label="Phone #",
    )


class AssetForm(forms.Form):
    name = "asset"
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
