from django.contrib.auth import get_user_model
from django.db import models


class WialonAccount(models.Model):
    """A Wialon resource/account."""

    name = models.CharField(max_length=128)
    """The name of the Wialon account."""
    wialon_id = models.IntegerField()
    """The Wialon id for the Wialon account."""

    def __str__(self) -> str:
        return self.name


class WialonAsset(models.Model):
    """A Wialon unit."""

    name = models.CharField(max_length=128)
    """The name of the Wialon unit."""
    wialon_id = models.IntegerField()
    """The Wialon id for the unit."""
    account = models.ForeignKey(
        "terminusgps_install.WialonAccount",
        on_delete=models.CASCADE,
        related_name="assets",
    )
    """The Wialon account bound to the unit."""

    def __str__(self) -> str:
        return self.name


class Installer(models.Model):
    """A human that installs units into vehicles."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    wialon_id = models.IntegerField(null=True, blank=True, default=None)
    """A Wialon user id for the installer."""
    accounts = models.ManyToManyField(
        "terminusgps_install.WialonAccount", related_name="accounts"
    )
    """Accounts the installer has access to."""

    def __str__(self) -> str:
        return self.user.username
