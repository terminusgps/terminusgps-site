from django import forms
from django.forms import widgets

from terminusgps_tracker.models import TrackerSubscriptionTier


class SubscriptionDeletionForm(forms.Form):
    subscription_id = forms.IntegerField(widget=widgets.HiddenInput())


class SubscriptionModificationForm(forms.Form):
    tier = forms.ModelChoiceField(queryset=TrackerSubscriptionTier.objects.all()[:3])


class SubscriptionConfirmationForm(forms.Form):
    payment_id = forms.CharField(max_length=9, required=False)
    address_id = forms.CharField(max_length=9, required=False)
