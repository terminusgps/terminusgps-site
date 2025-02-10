from authorizenet.apicontractsv1 import creditCardType, customerAddressType, paymentType
from django import forms
from django.db import models

from terminusgps.authorizenet.profiles.payments import PaymentProfile


class TrackerPaymentMethod(models.Model):
    default = models.BooleanField(default=False)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="payments",
    )

    class Meta:
        verbose_name = "payment method"
        verbose_name_plural = "payment methods"

    def __str__(self) -> str:
        return f"Payment Method #{self.authorizenet_id}"

    def save(self, form: forms.Form | None = None, **kwargs) -> None:
        if not self.authorizenet_id:
            if form and form.is_valid():
                assert self.profile.authorizenet_id, (
                    f"Authorizenet customer profile was not set for '{self.profile}'"
                )
                print(f"{form.cleaned_data["credit_card"].expirationDate = }")
                address = customerAddressType(
                    firstName=form.cleaned_data["first_name"],
                    lastName=form.cleaned_data["last_name"],
                    address=form.cleaned_data["address"]["street"],
                    city=form.cleaned_data["address"]["city"],
                    state=form.cleaned_data["address"]["state"],
                    country=form.cleaned_data["address"]["country"],
                    zip=form.cleaned_data["address"]["zip"],
                    phoneNumber=form.cleaned_data["phone"],
                )
                payment_profile = PaymentProfile(
                    billing_addr=address,
                    customer_profile_id=self.profile.authorizenet_id,
                    default=form.cleaned_data["default"],
                    merchant_id=self.profile.user.pk,
                    payment=paymentType(creditCard=form.cleaned_data["credit_card"]),
                )

                self.default = form.cleaned_data["default"]
                self.authorizenet_id = payment_profile.id
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        self.payment_profile.delete()
        return super().delete(*args, **kwargs)

    @property
    def payment_profile(self) -> PaymentProfile:
        return PaymentProfile(
            customer_profile_id=self.profile.authorizenet_id,
            default=self.default,
            merchant_id=self.profile.pk,
            id=self.authorizenet_id,
        )
