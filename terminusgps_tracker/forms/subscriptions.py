from django import forms
from django.forms import ModelForm, widgets

from terminusgps_tracker.models import TrackerSubscription


class SubscriptionCreationForm(forms.Form):
    subscription_tier = forms.ChoiceField(
        choices=TrackerSubscription.SubscriptionTier.choices,
        widget=widgets.Select(attrs={"class": "w-full bg-white mb-4 p-2"}),
    )


class SubscriptionDeletionForm(ModelForm):
    class Meta:
        model = TrackerSubscription
        fields = ["tier"]


class SubscriptionModificationForm(ModelForm):
    class Meta:
        model = TrackerSubscription
        fields = ["tier"]
