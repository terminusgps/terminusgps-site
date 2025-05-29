from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession


class Installer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""

    class Meta:
        verbose_name = _("installer")
        verbose_name_plural = _("installers")

    def __str__(self) -> str:
        return self.user.username


class InstallJob(models.Model):
    installer = models.ForeignKey(
        "terminusgps_installer.Installer", on_delete=models.CASCADE, related_name="jobs"
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
    """Wialon assets for the install job."""
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
        return f"Job #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse("installer:job detail", kwargs={"pk": self.pk})


class WialonAccount(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon resource/account id."""
    name = models.CharField(max_length=128)
    """Wialon account name."""

    class Meta:
        verbose_name = _("account")
        verbose_name_plural = _("accounts")

    def __str__(self) -> str:
        return self.name


class WialonAsset(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon asset id."""
    name = models.CharField(max_length=128)
    """Wialon asset name."""
    imei = models.CharField(max_length=19)
    """Wialon asset IMEI #."""

    class Meta:
        verbose_name = _("asset")
        verbose_name_plural = _("assets")

    def __str__(self) -> str:
        return self.name

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        super().save(**kwargs)
        if session and self._wialon_commands_need_sync(session):
            self._wialon_sync_commands(session)

    def get_absolute_url(self) -> str:
        return reverse_lazy("installer:asset detail", kwargs={"pk": self.pk})

    def get_icon_url(self, border: int = 32) -> str:
        return f"http://hst-api.wialon.com/avl_item_image/{self.pk}/{border}/icon.png"

    @transaction.atomic
    def _wialon_sync_commands(self, session: WialonSession) -> list:
        new_command_objs = [
            WialonAssetCommand(cmd_id=cmd_id, name=name, asset=self)
            for cmd_id, name in self._wialon_get_available_commands(session).items()
            if cmd_id not in self._wialon_get_existing_command_ids()
        ]
        if new_command_objs:
            created_commands = WialonAssetCommand.objects.bulk_create(
                new_command_objs, ignore_conflicts=True
            )
            return created_commands
        return []

    @transaction.atomic
    def _wialon_commands_need_sync(self, session: WialonSession) -> bool:
        existing_commands = self.commands.all()
        available_commands = self._wialon_get_available_commands(session)

        if existing_commands.count() == 0:
            return True
        return (
            existing_commands.count() != len(available_commands)
            if available_commands
            else False
        )

    def _wialon_get_existing_command_ids(self) -> set[int]:
        return set(
            WialonAssetCommand.objects.filter(asset=self).values_list(
                "cmd_id", flat=True
            )
        )

    def _wialon_get_available_commands(self, session: WialonSession) -> dict[str, int]:
        unit = WialonUnit(id=self.id, session=session)
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
    message = models.CharField(max_length=128, null=True, blank=True, default=None)
    """Message to send with the command."""

    class Meta:
        verbose_name = _("asset command")
        verbose_name_plural = _("asset commands")
        unique_together = ("asset", "cmd_id")

    def __str__(self) -> str:
        return self.name

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if session and self._wialon_needs_sync():
            self._wialon_sync(session)
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse(
            "installer:command detail",
            kwargs={"asset_pk": self.asset.pk, "pk": self.pk},
        )

    def get_execute_url(self) -> str:
        return reverse(
            "installer:command execute",
            kwargs={"asset_pk": self.asset.pk, "pk": self.pk},
        )

    def execute(
        self, session: WialonSession, link_type: str = "", timeout: int = 30
    ) -> None:
        session.wialon_api.unit_exec_cmd(
            **{
                "itemId": self.asset.pk,
                "commandName": self.name,
                "linkType": link_type,
                "timeout": timeout,
                "param": self.message,
            }
        )

    def _wialon_needs_sync(self) -> bool:
        return bool(self.message)

    @transaction.atomic
    def _wialon_sync(self, session: WialonSession) -> None:
        response = session.wialon_api.unit_get_command_definition_data(
            **{"itemId": self.asset.pk, "col": [self.cmd_id]}
        )[0]
        self.message = response.get("p")
        self.cmd_type = response.get("c")
