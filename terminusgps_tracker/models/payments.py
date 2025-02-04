from authorizenet.apicontractsv1 import paymentType
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
                self.default = form.cleaned_data["default"]
                self.authorizenet_id = PaymentProfile(
                    billing_addr=form.cleaned_data["address"],
                    customer_profile_id=self.profile.authorizenet_id,
                    default=form.cleaned_data["default"],
                    merchant_id=self.profile.user.pk,
                    payment=paymentType(creditCard=form.cleaned_data["credit_card"]),
                ).id
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
