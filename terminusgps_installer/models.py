from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from loguru import logger
from terminusgps.wialon.items import WialonResource, WialonUnit
from terminusgps.wialon.session import WialonSession

logger.enable("terminusgps.wialon.session")
logger.level("DEBUG") if settings.DEBUG else logger.level("WARNING")


class Installer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""
    accounts = models.ManyToManyField(
        "terminusgps_installer.WialonAccount",
        related_name="accounts",
        default=None,
        blank=True,
    )
    """Wialon accounts the installer has access to."""

    class Meta:
        verbose_name = _("installer")
        verbose_name_plural = _("installers")

    def __str__(self) -> str:
        """Returns the username for the installer user."""
        return self.user.username


class InstallJob(models.Model):
    installer = models.ForeignKey(
        "terminusgps_installer.Installer",
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    """An installer assigned to the install job."""
    account = models.ForeignKey(
        "terminusgps_installer.WialonAccount",
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    """A Wialon account for the install job."""
    asset = models.ForeignKey(
        "terminusgps_installer.WialonAsset",
        on_delete=models.PROTECT,
        related_name="job",
    )
    """Wialon asset for the install job."""
    date_created = models.DateTimeField(auto_now_add=True)
    """Date install job was created."""
    date_modified = models.DateTimeField(auto_now=True)
    """Date install job was last modified."""
    completed = models.BooleanField(default=False)
    """Whether or not the install job is complete."""

    class Meta:
        verbose_name = _("install job")
        verbose_name_plural = _("install jobs")

    def __str__(self) -> str:
        """Returns the job in format: 'Job #<pk>'."""
        return f"Job #{self.pk}"

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the install job's detail view."""
        return reverse("installer:job detail", kwargs={"job_pk": self.pk})

    def get_complete_url(self) -> str:
        """Returns a URL pointing to the install job's completion view."""
        return reverse("installer:job complete", kwargs={"job_pk": self.pk})


class WialonAccount(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon account id."""
    name = models.CharField(
        max_length=128, null=True, blank=True, default=None
    )
    """Wialon account name."""
    uid = models.IntegerField(null=True, blank=True, default=None)
    """Wialon account user id."""

    class Meta:
        verbose_name = _("account")
        verbose_name_plural = _("accounts")

    def __str__(self) -> str:
        """Returns the account id or name."""
        return self.name if self.name else str(self.pk)

    @transaction.atomic
    def wialon_sync(self, session: WialonSession) -> None:
        """
        Syncs the account's data with the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self._wialon_sync_data(session)

    @transaction.atomic
    def _wialon_sync_data(self, session: WialonSession) -> None:
        """
        Updates and sets :py:attr:`name` and :py:attr:`uid` using the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        resource = WialonResource(id=self.pk, session=session)
        self.name = resource.name
        self.uid = resource.creator_id


class WialonAsset(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon asset id."""
    name = models.CharField(max_length=128)
    """Wialon asset name."""
    imei = models.CharField(max_length=19, default=None, blank=True, null=True)
    """Wialon asset IMEI #."""
    vin = models.CharField(max_length=17, default=None, blank=True, null=True)
    """Wialon asset VIN #."""

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")

    def __str__(self) -> str:
        """Returns the asset's name."""
        return self.name

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the asset's detail view."""
        return reverse_lazy(
            "installer:asset detail", kwargs={"asset_pk": self.pk}
        )

    def get_update_url(self) -> str:
        """Returns a URL pointing to the asset's update view."""
        return reverse_lazy(
            "installer:asset update", kwargs={"asset_pk": self.pk}
        )

    def get_command_list_url(self) -> str:
        """Returns a URL pointing to the asset's command list view."""
        return reverse_lazy(
            "installer:command list", kwargs={"asset_pk": self.pk}
        )

    @transaction.atomic
    def wialon_sync(self, session: WialonSession) -> None:
        """
        Syncs the asset's data with the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        unit = WialonUnit(id=self.pk, session=session)
        self._wialon_sync_data(unit)
        self._wialon_sync_commands(unit)

    @transaction.atomic
    def _wialon_sync_data(self, unit: WialonUnit) -> None:
        """
        Updates and sets :py:attr:`name` and :py:attr:`imei` using the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self.name = unit.name
        self.imei = unit.imei_number
        self.vin = unit.pfields.get("vin")

    @transaction.atomic
    def _wialon_sync_commands(self, unit: WialonUnit) -> None:
        """
        Syncs asset command data with the Wialon API.

        :param unit: A Wialon unit.
        :type unit: :py:obj:`~terminusgps.wialon.items.units.WialonUnit`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        available_commands = self._wialon_get_available_commands(unit).items()
        existing_command_ids = self._wialon_get_existing_command_ids()

        new_command_objs = [
            WialonAssetCommand(cmd_id=cmd_id, name=name, asset=self)
            for cmd_id, name in available_commands
            if cmd_id not in existing_command_ids
        ]
        if new_command_objs:
            WialonAssetCommand.objects.bulk_create(
                new_command_objs, ignore_conflicts=True
            )

    def _wialon_get_existing_command_ids(self) -> set[int]:
        """Returns a set of :model:`terminusgps_installer.WialonAssetCommand` ids present in the database."""
        return set(
            WialonAssetCommand.objects.filter(asset=self).values_list(
                "cmd_id", flat=True
            )
        )

    @staticmethod
    def _wialon_get_available_commands(unit: WialonUnit) -> dict[int, str]:
        """
        Returns a dictionary of commands assigned to the asset in Wialon.

        :param unit: A Wialon unit.
        :type unit: :py:obj:`~terminusgps.wialon.items.units.WialonUnit`
        :returns: A dictionary of commands assigned to the asset.
        :rtype: :py:obj:`dict`

        Response format:

        +----------------+---------------+
        | key            | value         |
        +================+===============+
        | Command ID     | Command Name  |
        +----------------+---------------+

        """
        return {
            cmd["id"]: cmd["n"]
            for cmd in unit.available_commands.values()
            if cmd.get("id") and cmd.get("n")
        }


class WialonAssetCommand(models.Model):
    class WialonAssetCommandType(models.TextChoices):
        BLOCK_ENGINE = "block_engine", _("Block Engine")
        """Block engine."""
        UNBLOCK_ENGINE = "unblock_engine", _("Unblock Engine")
        """Unblock engine."""
        CUSTOM_MESSAGE = "custom_msg", _("Custom Message")
        """Custom message."""
        DRIVER_MESSAGE = "driver_msg", _("Driver Message")
        """Message to the driver."""
        DOWNLOAD_MESSAGES = "download_msgs", _("Download Messages")
        """Download messages."""
        QUERY_POSITION = "query_pos", _("Query Position")
        """Request coordinates."""
        QUERY_PHOTO = "query_photo", _("Query Photo")
        """Request a photo."""
        OUTPUT_ON = "output_on", _("Output On")
        """Activate output."""
        OUTPUT_OFF = "output_off", _("Output Off")
        """Deactivate output."""
        SEND_POSITION = "send_pos", _("Send Position")
        """Send coordinates."""
        SET_REPORT_INTERVAL = "set_report_interval", _("Set Report Interval")
        """Set the interval for sending data."""
        UPLOAD_CONFIG = "upload_cfg", _("Upload Configuration")
        """Upload configuration."""
        UPLOAD_FIRMWARE = "upload_sw", _("Upload Firmware")
        """Upload firmware."""

    class WialonAssetCommandLinkType(models.TextChoices):
        AUTO = "", _("Auto")
        """Deliver with an automatically determined protocol."""
        TCP = "tcp", _("TCP")
        """Deliver using TCP protocol."""
        UDP = "udp", _("UDP")
        """Deliver using UDP protocol."""
        VRT = "vrt", _("Virtual")
        """Deliver using a virtual protocol."""
        GSM = "gsm", _("GSM/SMS")
        """Deliver using gsm/sms protocol."""

    cmd_id = models.PositiveBigIntegerField()
    """Wialon asset command id."""
    cmd_type = models.CharField(
        max_length=64,
        choices=WialonAssetCommandType.choices,
        default=WialonAssetCommandType.CUSTOM_MESSAGE,
    )
    """Wialon asset command type."""
    name = models.CharField(max_length=64)
    """Wialon asset command name."""
    asset = models.ForeignKey(
        "terminusgps_installer.WialonAsset",
        on_delete=models.CASCADE,
        related_name="commands",
    )
    """Associated asset for the command."""
    message = models.CharField(
        max_length=128, null=True, blank=True, default=None
    )
    """Message to send with the command."""

    class Meta:
        verbose_name = _("asset command")
        verbose_name_plural = _("asset commands")
        unique_together = ("asset", "cmd_id")

    def __str__(self) -> str:
        """Returns the name of the command."""
        return self.name

    def get_absolute_url(self) -> str:
        """Returns a URL pointing to the command's detail view."""
        return reverse(
            "installer:command detail",
            kwargs={"asset_pk": self.asset.pk, "cmd_pk": self.pk},
        )

    def get_execute_url(self) -> str:
        """Returns a URL pointing to the command's execution view."""
        return reverse(
            "installer:command execute",
            kwargs={"asset_pk": self.asset.pk, "cmd_pk": self.pk},
        )

    def execute(
        self, session: WialonSession, link_type: str = "", timeout: int = 30
    ) -> None:
        """
        Executes the command using the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :param link_type: Protocol for command delivery. Default is :py:obj:`""` (auto).
        :type link_type: :py:obj:`str`
        :param timeout: How long (in seconds) the command should be queued for before execution. Default is :py:obj:`30`.
        :type timeout: :py:obj:`int`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        session.wialon_api.unit_exec_cmd(
            **{
                "itemId": self.asset.pk,
                "commandName": self.name,
                "linkType": link_type,
                "timeout": timeout,
                "param": self.message,
            }
        )

    @transaction.atomic
    def wialon_sync(self, session: WialonSession) -> None:
        """
        Syncs the command's data with the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        self._wialon_sync_data(session)

    @transaction.atomic
    def _wialon_sync_data(self, session: WialonSession) -> None:
        """
        Updates and sets :py:attr:`message` and :py:attr:`cmd_type` using the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        response = session.wialon_api.unit_get_command_definition_data(
            **{"itemId": self.asset.pk, "col": [self.cmd_id]}
        )[0]
        self.message = response.get("p")
        self.cmd_type = response.get("c")
