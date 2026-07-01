from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class ContactForm(forms.ModelForm):
    class Meta:
        model = models.ContactFormResponse
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.widgets.TextInput(
                attrs={
                    "autofocus": "on",
                    "autocomplete": "name",
                    "placeholder": "Your Name",
                }
            ),
            "email": forms.widgets.EmailInput(
                attrs={
                    "autocomplete": "email",
                    "placeholder": "email@domain.com",
                }
            ),
            "message": forms.widgets.Textarea(
                attrs={"placeholder": "What's crackin', Terminus GPS?"}
            ),
        }
        help_texts = {
            "name": _("Provide your full name so we know what to call you."),
            "email": _("Provide a good email for us to get back to you at."),
        }
