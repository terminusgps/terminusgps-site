from django import forms

from terminusgps_tracker.models import TrackerSubscription
from terminusgps_tracker.models.subscriptions import TrackerSubscriptionTier


class SubscriptionCancelForm(forms.Form):
    subscription = forms.ModelChoiceField(
        queryset=TrackerSubscription.objects.all(), required=True
    )


class SubscriptionUpdateForm(forms.Form):
    subscription = forms.ModelChoiceField(queryset=TrackerSubscription.objects.all())
    tier = forms.ModelChoiceField(
        queryset=TrackerSubscriptionTier.objects.filter(pk__in=[1, 2, 3]),
        required=True,
        initial=2,
    )
    payment_id = forms.CharField(max_length=9, required=False)
    address_id = forms.CharField(max_length=9, required=False)
