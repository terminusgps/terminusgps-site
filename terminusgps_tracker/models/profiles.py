from django.contrib.auth import get_user_model
from django.db import models

from terminusgps.authorizenet.profiles.customers import CustomerProfile
from terminusgps_tracker.validators import (
    validate_wialon_resource_id,
    validate_wialon_unit_group_id,
    validate_wialon_user_id,
)


class TrackerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    authorizenet_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True
    )
    wialon_group_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True, validators=[validate_wialon_unit_group_id]
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True, validators=[validate_wialon_resource_id]
    )
    wialon_end_user_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True, validators=[validate_wialon_user_id]
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True, validators=[validate_wialon_user_id]
    )

    class Meta:
        verbose_name = "profile"
        verbose_name_plural = "profiles"

    def __str__(self) -> str:
        return f"{self.user}'s Profile"

    def save(self, **kwargs) -> None:
        if not self.authorizenet_id:
            self.authorizenet_id = CustomerProfile(
                merchant_id=self.user.pk,
                email=self.user.username,
                desc=f"{__package__} - TrackerProfile #{self.user.pk}",
            ).id
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        self.customer_profile.delete()
        return super().delete(*args, **kwargs)

    @property
    def customer_profile(self) -> CustomerProfile:
        return CustomerProfile(merchant_id=self.user.pk, id=self.authorizenet_id)
