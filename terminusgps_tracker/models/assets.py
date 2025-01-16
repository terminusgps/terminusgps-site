from django.db import models, transaction

from django.urls import reverse
import terminusgps.wialon.flags as flags
from terminusgps.wialon.constants import WialonCommandType, WialonCommandLink
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid
from django.conf import settings


class TrackerAssetCommand(models.Model):
    name = models.CharField(max_length=128)
    link = models.CharField(
        max_length=64,
        choices=WialonCommandLink.choices,
        default=WialonCommandLink.AUTO,
        blank=True,
    )
    type = models.CharField(
        max_length=64,
        choices=WialonCommandType.choices,
        default=WialonCommandType.CUSTOM_MSG,
    )

    class Meta:
        verbose_name = "command"
        verbose_name_plural = "commands"

    def __str__(self) -> str:
        return self.name

    def execute(
        self,
        id: int,
        session: WialonSession,
        params: dict | None = None,
        flags: int = 0,
    ) -> None:
        session.wialon_api.unit_exec_cmd(
            **{
                "itemId": str(id),
                "commandName": self.name,
                "linkType": self.link,
                "param": params if params else {},
                "flags": flags,
            }
        )


class TrackerAsset(models.Model):
    wialon_id = models.PositiveIntegerField(default=None, blank=True, null=True)
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="assets",
        null=True,
    )
    commands = models.ManyToManyField(
        "terminusgps_tracker.TrackerAssetCommand", default=None, blank=True
    )

    # Wialon data
    name = models.CharField(max_length=64, default=None, null=True, blank=True)
    hw_type = models.CharField(max_length=64, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=64, default=None, null=True, blank=True)
    imei_number = models.PositiveIntegerField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"

    def __str__(self) -> str:
        return str(self.name)

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if session and self.imei_number and not self.wialon_id:
            self.wialon_id = get_id_from_iccid(self.imei_number, session)
            self.populate(session)
        elif session:
            self.populate(session)
        super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse("asset detail", kwargs={"pk": self.pk})

    @transaction.atomic
    def populate(self, session: WialonSession) -> None:
        assert self.wialon_id, "No Wialon id was set"
        data = session.wialon_api.core_search_item(
            **{
                "id": self.wialon_id,
                "flags": sum(
                    [flags.DATAFLAG_UNIT_BASE, flags.DATAFLAG_UNIT_ADVANCED_PROPERTIES]
                ),
            }
        )["item"]
        self.name = data.get("nm")
        self.hw_type = data.get("cls")
        self.imei_number = data.get("uid")
        self.phone_number = data.get("ph")
        self.is_active = bool(data.get("act", 0))
