from django.db import models, transaction
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup
from terminusgps.wialon.session import WialonSession
from django.conf import settings
import terminusgps.wialon.flags as flags


class TrackerAsset(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="assets",
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
        if session is not None:
            self.populate(session)
            self._pop_off_unactivated_group(session)
        return super().save(**kwargs)

    def execute_command(
        self, name: str, session: WialonSession, params: dict | None = None
    ) -> None:
        session.wialon_api.unit_exec_cmd(
            **{
                "itemId": self.id,
                "commandName": name,
                "linkType": "",
                "param": params if params else {},
                "flags": 0,
            }
        )

    def _pop_off_unactivated_group(self, session: WialonSession) -> None:
        unactivated = WialonUnitGroup(
            id=str(settings.WIALON_UNACTIVATED_GROUP), session=session
        )
        unit = WialonUnit(id=str(self.id), session=session)
        if unit.id in unactivated.items:
            unactivated.rm_item(unit)

    @transaction.atomic
    def populate(self, session: WialonSession) -> None:
        data = session.wialon_api.core_search_item(
            **{
                "id": self.id,
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
