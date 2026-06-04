from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


class TerminusProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="terminus_profile",
    )
    wialon_user_id = models.CharField(blank=True)
    authorizenet_profile_id = models.CharField(blank=True)
    authorizenet_subscription_id = models.CharField(blank=True)

    class Meta:
        verbose_name = _("terminus profile")
        verbose_name_plural = _("terminus profiles")

    def __str__(self) -> str:
        return str(self.user)
