from django import forms
from django.forms import widgets


class EmailInquiryForm(forms.Form):
    default_css_class = (
        "w-full block rounded p-2 dark:bg-gray-600 dark:text-gray-100 bg-white"
    )
    email = forms.EmailField(
        widget=widgets.EmailInput(
            attrs={"class": default_css_class, "placeholder": "Your Email Address"}
        )
    )
    text = forms.CharField(
        widget=widgets.Textarea(
            attrs={
                "rows": 12,
                "cols": 40,
                "class": default_css_class,
                "placeholder": "Let's work together on...",
            }
        )
    )


class EmailNewsletterForm(forms.Form):
    email = forms.EmailField()
