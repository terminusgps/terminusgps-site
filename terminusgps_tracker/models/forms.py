from django import forms


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
        help_text="Enter your first name.",
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
        help_text="Enter your last name.",
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        help_text="Enter your email address.",
    )
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        label="Phone #",
        help_text="Enter a U.S. phone number.",
    )
    asset_name = forms.CharField(
        max_length=255,
        required=True,
        label="Asset Name",
        help_text="Enter a name for your TerminusGPS asset.",
    )
    imei_number = forms.CharField(
        max_length=20,
        required=True,
        disabled=True,
        label="IMEI #",
        help_text="The IMEI number for your TerminusGPS asset.",
    )
