from django.contrib.auth import get_user_model
from django.db import models


class WialonAccount(models.Model):
    """
    A Wialon resource/account.

    `Wialon account reference <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/account/account>`_

    """

    name = models.CharField(max_length=128)
    """The name of the Wialon account."""
    wialon_id = models.IntegerField()
    """The wialon id for the account."""

    def __str__(self) -> str:
        """Returns the name of the Wialon account."""
        return self.name


class WialonAsset(models.Model):
    """
    A Wialon unit.

    `Wialon unit reference <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/unit/unit>`_

    """

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
        """Returns the Wialon unit name."""
        return self.name


class Installer(models.Model):
    """
    A human that installs GPS tracking units into vehicles.

    `Wialon user reference <https://sdk.wialon.com/wiki/en/sidebar/remoteapi/apiref/user/user>`_

    """

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    wialon_id = models.IntegerField(null=True, blank=True, default=None)
    """A Wialon user id for the installer."""
    accounts = models.ManyToManyField(
        "terminusgps_install.WialonAccount", related_name="installers"
    )
    """Wialon accounts the installer has access to."""

    def __str__(self) -> str:
        """Returns the username for the installer."""
        return self.user.username
