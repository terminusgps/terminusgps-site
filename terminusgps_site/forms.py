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
                    "class": "peer p-2 border border-current bg-stone-50 rounded w-full user-valid:text-green-700 user-invalid:text-red-700 dark:bg-gray-500 dark:user-valid:text-green-300 dark:user-invalid:text-red-300",
                }
            ),
            "email": forms.widgets.EmailInput(
                attrs={
                    "autocomplete": "email",
                    "placeholder": "email@domain.com",
                    "class": "peer p-2 border border-current bg-stone-50 rounded w-full user-valid:text-green-700 user-invalid:text-red-700 dark:bg-gray-500 dark:user-valid:text-green-300 dark:user-invalid:text-red-300",
                }
            ),
            "message": forms.widgets.Textarea(
                attrs={
                    "class": "peer p-2 border border-current bg-stone-50 rounded w-full user-valid:text-green-700 user-invalid:text-red-700 dark:bg-gray-500 dark:user-valid:text-green-300 dark:user-invalid:text-red-300"
                }
            ),
        }
        help_texts = {
            "name": _("Provide your full name so we know what to call you."),
            "email": _("Provide a good email for us to get back to you at."),
        }
