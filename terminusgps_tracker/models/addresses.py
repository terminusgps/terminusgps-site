from authorizenet.apicontractsv1 import customerAddressType
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
                address_profile = AddressProfile(
                    customer_profile_id=self.profile.authorizenet_id,
                    default=form.cleaned_data["default"],
                    merchant_id=self.profile.user.pk,
                    shipping_addr=address,
                )
                self.default = form.cleaned_data["default"]
                self.authorizenet_id = address_profile.id
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
