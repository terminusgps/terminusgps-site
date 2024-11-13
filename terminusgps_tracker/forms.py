from django import forms
from django.core.validators import validate_email
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import widgets
from django.forms.models import ModelForm

from terminusgps_tracker.models.notification import TrackerNotification
from terminusgps_tracker.models.subscription import TrackerSubscription
from terminusgps_tracker.validators import (
    validate_wialon_imei_number,
    validate_wialon_password,
    validate_wialon_unit_name,
    validate_wialon_username,
)


class TrackerRegistrationForm(UserCreationForm):
    field_order = ["first_name", "last_name", "username", "password1", "password2"]

    first_name = forms.CharField(
        label="First Name",
        max_length=64,
        widget=widgets.TextInput(attrs={"placeholder": "First"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=64,
        widget=widgets.TextInput(attrs={"placeholder": "Last"}),
    )
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email, validate_wialon_username],
        widget=widgets.EmailInput(attrs={"placeholder": "email@terminusgps.com"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=widgets.PasswordInput(),
        validators=[validate_wialon_password],
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=widgets.PasswordInput(),
        validators=[validate_wialon_password],
    )


class TrackerAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email Address",
        min_length=4,
        max_length=150,
        validators=[validate_email],
        widget=widgets.EmailInput(
            attrs={
                "class": "w-full block my-4 p-2 rounded-md",
                "placeholder": "email@terminusgps.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        min_length=8,
        max_length=32,
        widget=widgets.PasswordInput(
            attrs={"class": "w-full block my-4 p-2 rounded-md"}
        ),
    )


class AssetCreationForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=widgets.TextInput(
            attrs={
                "class": "w-full block my-4 p-2 rounded-md",
                "placeholder": "My Vehicle",
            }
        ),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=widgets.NumberInput(
            attrs={
                "placeholder": "555555555555",
                "class": "w-full block my-4 p-2 rounded-md",
            }
        ),
        min_length=15,
        max_length=24,
    )


class AssetModificationForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=widgets.TextInput({"placeholder": "My Vehicle"}),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=widgets.NumberInput({"placeholder": "123412341234"}),
        min_length=15,
        max_length=24,
    )


class AssetDeletionForm(forms.Form):
    asset_name = forms.CharField(
        label="Asset Name",
        validators=[validate_wialon_unit_name],
        widget=widgets.TextInput({"placeholder": "My Vehicle"}),
        min_length=4,
        max_length=64,
    )
    imei_number = forms.CharField(
        label="IMEI #",
        validators=[validate_wialon_imei_number],
        widget=widgets.NumberInput({"placeholder": "123412341234"}),
        min_length=15,
        max_length=24,
    )


class PaymentMethodCreationForm(forms.Form):
    credit_card_number = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    credit_card_expiry_month = forms.CharField(
        min_length=2,
        max_length=2,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    credit_card_expiry_year = forms.CharField(
        min_length=2,
        max_length=2,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    credit_card_ccv = forms.CharField(
        min_length=3,
        max_length=4,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    address_street = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    address_city = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    address_state = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    address_zip = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    address_country = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )
    address_phone = forms.CharField(
        min_length=12,
        max_length=16,
        widget=widgets.TextInput(attrs={"class": "w-full bg-white"}),
    )


class PaymentMethodDeletionForm(forms.Form): ...


class NotificationCreationForm(ModelForm):
    class Meta:
        model = TrackerNotification
        fields = ["method"]


class NotificationModificationForm(forms.Form):
    class Meta:
        model = TrackerNotification
        fields = ["method"]


class NotificationDeletionForm(forms.Form):
    class Meta:
        model = TrackerNotification
        fields = ["method"]


class SubscriptionCreationForm(ModelForm):
    class Meta:
        model = TrackerSubscription
        fields = ["tier"]


class SubscriptionDeletionForm(ModelForm):
    class Meta:
        model = TrackerSubscription
        fields = ["tier"]


class SubscriptionModificationForm(ModelForm):
    class Meta:
        model = TrackerSubscription
        fields = ["tier"]
