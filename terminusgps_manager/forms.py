from djang


class SubscriptionCreateForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["aprofile", "pprofile"]
