from django import forms

from terminusgps_tracker.models import Customer


class CustomerPaymentMethodChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        profile = obj.get_authorizenet_profile()
        if profile is not None and all(
            [
                hasattr(profile, "paymentProfile"),
                hasattr(profile.paymentProfile, "payment"),
                hasattr(profile.paymentProfile.payment, "creditCard"),
                hasattr(
                    profile.paymentProfile.payment.creditCard, "cardNumber"
                ),
                hasattr(profile.paymentProfile.payment.creditCard, "cardType"),
            ]
        ):
            cc_type = str(profile.paymentProfile.payment.creditCard.cardType)
            cc_num = str(profile.paymentProfile.payment.creditCard.cardNumber)
            return f"{cc_type} ending in {cc_num[-4:]}"
        return str(obj)


class CustomerShippingAddressChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        profile = obj.get_authorizenet_profile()
        if profile is not None and all(
            [hasattr(profile, "address"), hasattr(profile.address, "address")]
        ):
            return str(profile.address.address)
        return str(obj)


class CustomerSubscriptionCreationForm(forms.Form):
    def __init__(self, customer: Customer, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["address"].queryset = customer.addresses.all()
        self.fields["payment"].queryset = customer.payments.all()

    payment = CustomerPaymentMethodChoiceField(
        empty_label=None, label="Payment Method", queryset=None
    )
    address = CustomerShippingAddressChoiceField(
        empty_label=None, label="Shipping Address", queryset=None
    )


class CustomerSubscriptionUpdateForm(forms.Form):
    def __init__(self, customer: Customer, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["address"].queryset = customer.addresses.all()
        self.fields["payment"].queryset = customer.payments.all()

    payment = CustomerPaymentMethodChoiceField(
        empty_label=None, label="Payment Method", queryset=None
    )
    address = CustomerShippingAddressChoiceField(
        empty_label=None, label="Shipping Address", queryset=None
    )
