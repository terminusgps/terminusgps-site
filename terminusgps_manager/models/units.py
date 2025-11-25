import typing
from collections.abc import Sequence

from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.session import WialonSession

from terminusgps_manager.models.base import WialonObject


class WialonUnit(WialonObject):
    """A Wialon unit."""

    class Meta:
        verbose_name = _("wialon unit")
        verbose_name_plural = _("wialon units")

    def set_active(
        self, session: WialonSession, *, enabled: bool = True
    ) -> dict[str, typing.Any]:
        """
        Enables or disables the unit.

        :param session: Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param enabled: Whether to enable or disable the unit. Default is :py:obj:`True` (enable the unit).
        :type enabled: bool
        :returns: An empty dictionary.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, typing.Any] = {}
        params["itemId"] = self.id
        params["active"] = int(enabled)
        return session.wialon_api.unit_set_active(**params)

    def get_last_message(
        self,
        session: WialonSession,
        *,
        sensor_ids: Sequence[int] | None = None,
        last_valid: bool = False,
    ) -> dict[str, typing.Any]:
        """
        Returns the unit's last message.

        :param session: Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param sensor_ids: A sequence of sensor ids. If not provided, returns all sensor values. Default is :py:obj:`None`.
        :type sensor_ids: ~collections.abc.Sequence[int] | None
        :param last_valid: Whether to calculate the sensor value using the last valid parameter. Default is :py:obj:`False`.
        :type last_valid: bool
        :returns: A dictionary containing unit sensors and their values.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, typing.Any] = {}
        params["unitId"] = self.id
        if sensor_ids is not None:
            params["sensor_ids"] = sensor_ids
        if last_valid:
            params["flags"] = int(last_valid)
        return session.wialon_api.unit_calc_last_message(**params)
