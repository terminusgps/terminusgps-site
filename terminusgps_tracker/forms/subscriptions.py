from django import forms
from django.forms import widgets

from terminusgps_tracker.models import TrackerSubscriptionTier


class SubscriptionCreationForm(forms.Form):
    tier = forms.ModelChoiceField(
        queryset=TrackerSubscriptionTier.objects.all()[:3],
        widget=widgets.Select(attrs={"class": "p-4 rounded-md mb-4 w-full bg-white"}),
    )


class SubscriptionDeletionForm(forms.Form):
    subscription_id = forms.IntegerField(widget=widgets.HiddenInput())


class SubscriptionModificationForm(forms.Form):
    tier = forms.ModelChoiceField(
        queryset=TrackerSubscriptionTier.objects.all()[:3],
        widget=widgets.Select(attrs={"class": "p-4 rounded-md mb-4 w-full bg-white"}),
    )
