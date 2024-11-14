from django import forms
from django.forms import ModelForm

from terminusgps_tracker.models import TrackerNotification


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
