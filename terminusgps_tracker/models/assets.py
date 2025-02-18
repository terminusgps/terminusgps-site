from django.db import models, transaction
from django.urls import reverse

from terminusgps.wialon.items import WialonUnit
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.validators import (
    validate_wialon_unit_name_unique,
    validate_wialon_unit_id,
)


class TrackerAsset(models.Model):
    wialon_id = models.CharField(max_length=8, validators=[validate_wialon_unit_id])
    profile = models.ForeignKey(
        "terminusgps_tracker.TrackerProfile",
        on_delete=models.CASCADE,
        related_name="assets",
        null=True,
    )
    name = models.CharField(
        max_length=64,
        default=None,
        null=True,
        blank=True,
        validators=[validate_wialon_unit_name_unique],
    )
    hw_type = models.CharField(max_length=64, default=None, null=True, blank=True)
    phone_number = models.CharField(max_length=64, default=None, null=True, blank=True)
    imei_number = models.CharField(max_length=64, default=None, null=True, blank=True)
    is_active = models.BooleanField(default=None, null=True, blank=True)

    class Meta:
        verbose_name = "asset"
        verbose_name_plural = "assets"

    def __str__(self) -> str:
        return str(self.name)

    def save(self, session: WialonSession | None = None, **kwargs) -> None:
        if session and self.wialon_id:
            self.populate(session)
        super().save(**kwargs)

    def get_absolute_url(self) -> str:
        return reverse("asset detail", kwargs={"pk": self.pk})

    def get_position(self, session: WialonSession) -> dict:
        return self.get_wialon_unit(session).get_position()

    def get_wialon_unit(self, session: WialonSession) -> WialonUnit:
        """
        Retrieves a :py:obj:`~terminusgps.wialon.items.WialonUnit` object for the asset.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises AssertionError: If the asset's wialon id was not set.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: A Wialon unit object.
        :rtype: :py:obj:`~terminusgps.wialon.items.WialonUnit`

        """
        assert self.wialon_id, "No Wialon id was set"
        return WialonUnit(id=self.wialon_id, session=session)

    @transaction.atomic
    def populate(self, session: WialonSession) -> None:
        """
        Populates the asset with data retrieved from the Wialon API.

        :param session: A valid Wialon API session.
        :type session: :py:obj:`~terminusgps.wialon.session.WialonSession`
        :raises AssertionError: If the asset's wialon id was not set.
        :raises WialonError: If something goes wrong with Wialon.
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        unit = self.get_wialon_unit(session)
        self.name = unit.name
        self.hw_type = unit.hw_type
        self.imei_number = unit.imei_number
        self.is_active = unit.active

        phones = unit.get_phone_numbers()
        if phones:
            self.phone_number = phones[0]
