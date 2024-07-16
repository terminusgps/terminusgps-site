import string

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.template.loader import render_to_string
from django.core import mail
from django.core.mail import EmailMessage

from terminusgps_tracker.wialonapi.session import WialonSession
from terminusgps_tracker.wialonapi.query import imei_number_exists_in_wialon

def validate_wialon_password(value: str) -> None:
    """Checks if the given value is a valid Wialon password."""
    valid_special_chars = set("!#$%-.:;@?_~")
    if not any(c in string.ascii_uppercase for c in value):
        raise ValidationError(
            _("Wialon password must contain at least one uppercase letter."),
            params={"value": value}
        )
    elif not any(c in string.ascii_lowercase for c in value):
        raise ValidationError(
            _("Wialon password must contain at least one lowercase letter."),
            params={"value": value}
        )
    elif not any(c in string.digits for c in value):
        raise ValidationError(
            _("Wialon password must contain at least one digit."),
            params={"value": value}
        )
    elif not any(c in valid_special_chars for c in value):
        raise ValidationError(
            _("Wialon password must contain at least one special symbol. Symbols: '%(symbols)s'"),
            params={"symbols": "".join(valid_special_chars)}
        )
    else:
        return None


def validate_imei_number_exists(value: str) -> None:
    """Checks if the given value is present in the TerminusGPS UUID database."""
    with WialonSession() as session:
        if not imei_number_exists_in_wialon(value, session):
            raise ValidationError(
                _(
                    "IMEI number '%(value)s' does not exist in the TerminusGPS database."
                ),
                params={"value": value},
            )


class RegistrationForm(forms.Form):
    field_template_name = "terminusgps_tracker/forms/field.html"
    initial = {}
    first_name = forms.CharField(
        max_length=255,
        required=True,
        label="First Name",
        help_text="Please enter your first name.",
    )
    last_name = forms.CharField(
        max_length=255,
        required=True,
        label="Last Name",
        help_text="Please enter your last name.",
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        help_text="Please enter your email address.",
    )
    asset_name = forms.CharField(
        max_length=255,
        required=True,
        label="Asset Name",
        help_text="Please enter a name for your new asset.",
    )
    wialon_password = forms.CharField(
        max_length=64,
        min_length=8,
        required=True,
        label="Wialon Password",
        validators=[validate_wialon_password],
        widget=forms.PasswordInput,
    )
    imei_number = forms.CharField(
        max_length=20,
        required=True,
        label="IMEI #",
        help_text="This should've been filled out for you. If not, please contact support@terminusgps.com",
        validators=[validate_imei_number_exists],
    )

    def send_creds_email(self, email: str, passw: str) -> None:
        """Sends a form's credentials via email."""
        context = {"username": email, "passw": passw}
        with mail.get_connection() as connection:
            msg = EmailMessage(
                subject="Your Credentials",
                body=render_to_string("terminusgps_tracker/email_credentials.html", context),
                from_email="support@terminusgps.com",
                to=[email],
                bcc=["pspeckman@terminusgps.com"],
                reply_to=["pspeckman@terminusgps.com", "support@terminusgps.com"],
                connection=connection,
            )
            msg.content_subtype = "html"
            msg.send()

    def get_absolute_url(self):
        return reverse("/forms/registration/", kwargs={"pk": self.pk})
