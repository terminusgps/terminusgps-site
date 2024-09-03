from django import forms

class RegistrationForm(forms.Form):
    imei_number = forms.CharField(
        label="IMEI #",
        min_length=4,
        max_length=17,
        required=True,
        disabled=True,
        help_text="You can find this underneath the QR Code you received with your vehicle."
    )
    email = forms.EmailField(
        label="Email Address",
        min_length=4,
        max_length=128,
        required=True,
        disabled=False,
        help_text="A good email address we can reach you at."
    )
    wialon_password_1 = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        required=True,
        disabled=False,
        widget=forms.PasswordInput()
    )
    wialon_password_2 = forms.CharField(
        label="Confirm Password",
        min_length=8,
        max_length=32,
        required=True,
        disabled=False,
        widget=forms.PasswordInput()
    )
