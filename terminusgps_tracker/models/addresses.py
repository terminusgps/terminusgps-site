from django import forms
from django.db import models

from terminusgps.authorizenet.profiles.addresses import AddressProfile


class TrackerShippingAddress(models.Model):
    default = models.BooleanField(default=False)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    class Meta:
        verbose_name = "shipping address"
        verbose_name_plural = "shipping addresses"

    def __str__(self) -> str:
        return f"Address #{self.authorizenet_id}"

    def save(self, form: forms.Form | None = None, **kwargs) -> None:
        if not self.authorizenet_id:
            if form and form.is_valid():
                assert self.profile.authorizenet_id, (
                    f"Authorizenet customer profile was not set for '{self.profile}'"
                )
                self.default = form.cleaned_data["default"]
                self.authorizenet_id = AddressProfile(
                    customer_profile_id=self.profile.authorizenet_id,
                    default=form.cleaned_data["default"],
                    merchant_id=self.profile.user.pk,
                    shipping_addr=form.cleaned_data["address"],
                ).id
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        self.address_profile.delete()
        return super().delete(*args, **kwargs)

    @property
    def address_profile(self) -> AddressProfile:
        return AddressProfile(
            customer_profile_id=self.profile.authorizenet_id,
            default=self.default,
            merchant_id=self.profile.pk,
            id=self.authorizenet_id,
        )
