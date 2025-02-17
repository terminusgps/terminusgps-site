from django.db import models, transaction

from django.urls import reverse
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import get_id_from_iccid
import terminusgps.wialon.flags as flags

from terminusgps_tracker.validators import (
    validate_wialon_unit_name_unique,
    validate_wialon_unit_id,
)


class TrackerAsset(models.Model):
    imei_number = models.PositiveIntegerField()
    wialon_id = models.PositiveIntegerField(
        default=None, blank=True, null=True, validators=[validate_wialon_unit_id]
    )
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="assets",
        null=True,
    )

    # Wialon data
    name = models.CharField(
        max_length=64,
        default=None,
        null=True,
        blank=True,
        validators=[validate_wialon_unit_name_unique],
    )
    hw_type = models.CharField(max_length=64, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=64, default=None, null=True, blank=True)

    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"

    def __str__(self) -> str:
        return str(self.name)

    def save(
        self, session: WialonSession | None = None, populate: bool = False, **kwargs
    ) -> None:
        if session and self.imei_number and not self.wialon_id:
            self.wialon_id = get_id_from_iccid(self.imei_number, session)
            self.populate(session)
        elif session and populate:
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
        self.phone_number = data.get("ph")
        self.is_active = bool(data.get("act", 0))
