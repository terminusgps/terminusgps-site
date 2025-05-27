from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.urls import reverse, reverse_lazy
from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession


class Installer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    """A Django user."""

    class Meta:
        verbose_name = "installer"
        verbose_name_plural = "installers"

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
        on_delete=models.CASCADE,
        related_name="job",
    )
    """Wialon assets for the install job."""
    date_created = models.DateTimeField(auto_now_add=True)
    """Date install job was created."""
    date_modified = models.DateTimeField(auto_now=True)
    """Date install job was last modified."""

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
        verbose_name = "account"
        verbose_name_plural = "accounts"

    def __str__(self) -> str:
        return self.name


class WialonAsset(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon asset id."""
    name = models.CharField(max_length=128)
    """Wialon asset name."""

    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"

    def __str__(self) -> str:
        return self.name

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if session and self._wialon_commands_need_sync(session):
            self._wialon_sync_commands(session)
        return super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse_lazy("installer:asset detail", kwargs={"pk": self.pk})

    @transaction.atomic
    def _wialon_sync_commands(self, session: WialonSession) -> list:
        new_command_objs = [
            WialonAssetCommand(id=cmd_id, name=name, asset=self)
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
        existing_count = self.commands.count()
        if existing_count == 0:
            return True

        available_commands = self._wialon_get_available_commands(session)
        if not available_commands:
            return False

        return existing_count != len(available_commands)

    def _wialon_get_existing_command_ids(self) -> set[int]:
        return set(
            WialonAssetCommand.objects.filter(asset=self).values_list("id", flat=True)
        )

    def _wialon_get_available_commands(self, session: WialonSession) -> dict[str, int]:
        unit = WialonUnit(id=self.id, session=session)
        return {
            cmd["id"]: cmd["n"]
            for cmd in unit.available_commands.values()
            if cmd.get("id") and cmd.get("n")
        }


class WialonAssetCommand(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    """Wialon asset command id."""
    name = models.CharField(max_length=64)
    """Wialon asset command name."""
    asset = models.ForeignKey(
        "terminusgps_installer.WialonAsset",
        on_delete=models.CASCADE,
        related_name="commands",
    )
    """Associated asset for the command."""

    class Meta:
        verbose_name = "asset command"
        verbose_name_plural = "asset commands"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse(
            "installer:command detail",
            kwargs={"asset_pk": self.asset.pk, "pk": self.pk},
        )

    def get_execution_url(self) -> str:
        return reverse(
            "installer:command execute",
            kwargs={"asset_pk": self.asset.pk, "pk": self.pk},
        )
