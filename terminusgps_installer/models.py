from django.contrib.auth import get_user_model
from django.db import models


class Installer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    accounts = models.ForeignKey(
        "terminusgps_installer.WialonAccount",
        on_delete=models.CASCADE,
        related_name="installers",
        null=True,
        blank=True,
        default=None,
    )
    """Wialon accounts assigned to the installer."""

    class Meta:
        verbose_name = "installer"
        verbose_name_plural = "installers"

    def __str__(self) -> str:
        return self.user.username


class WialonAccount(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon account id."""
    name = models.CharField(max_length=128)
    """Wialon account name."""

    class Meta:
        verbose_name = "account"
        verbose_name_plural = "accounts"

    def __str__(self) -> str:
        return self.name
