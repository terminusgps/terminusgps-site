from django.db import models
from django.contrib.auth import get_user_model


class CustomerProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    completed_registration = models.BooleanField(default=False)
    authorizenet_profile_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_payment_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_address_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    authorizenet_subscription_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_super_user_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, default=None
    )
    wialon_group_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )
    wialon_resource_id = models.PositiveBigIntegerField(
        unique=False, null=True, blank=True, default=None
    )

    def __str__(self) -> str:
        return f"{self.user.username}'s Profile"
