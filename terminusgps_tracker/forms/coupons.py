from django import forms

from terminusgps_tracker.models import CustomerCoupon


class CustomerCouponRedeemForm(forms.Form):
    coupon = forms.ModelChoiceField(queryset=CustomerCoupon.objects.all())
