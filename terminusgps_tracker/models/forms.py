from django import forms


class PersonForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
        help_text="Enter your first name.",
        template_name="terminusgps_tracker/register/field.html",
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
        help_text="Enter your last name.",
        template_name="terminusgps_tracker/register/field.html",
    )


class ContactForm(forms.Form):
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


class AssetForm(forms.Form):
    error_css_class = "bg-red-50 border border-red-500 text-red-900 placeholder-red-700 text-sm rounded-lg focus:ring-red-500 dark:bg-gray-700 focus:border-red-500 block w-full p-2.5 dark:text-red-500 dark:placeholder-red-500 dark:border-red-500"
    asset_name = forms.CharField(max_length=255, required=True)
    imei_number = forms.CharField(max_length=20, required=True, disabled=True)


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
        help_text="Enter your first name.",
        template_name="terminusgps_tracker/register/field.html",
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
        help_text="Enter your last name.",
        template_name="terminusgps_tracker/register/field.html",
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        help_text="Enter your email address.",
        template_name="terminusgps_tracker/register/field.html",
    )
    phone_number = forms.CharField(
        max_length=12,
        required=False,
        label="Phone #",
        help_text="Enter a U.S. phone number.",
        template_name="terminusgps_tracker/register/field.html",
    )
    asset_name = forms.CharField(max_length=255, required=True)
    imei_number = forms.CharField(max_length=20, required=True, disabled=True)
