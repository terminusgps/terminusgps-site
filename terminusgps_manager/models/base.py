import typing

from django.db import models
from terminusgps.wialon.session import WialonSession


class WialonObject(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self) -> str:
        """Returns the Wialon object name."""
        return self.name

    def get_data(
        self, session: WialonSession, *, flags: int = 0x1
    ) -> dict[str, typing.Any]:
        """
        Returns a dictionary of data for the Wialon object using the `core/search_item <https://help.wialon.com/en/api/user-guide/api-reference/core/search_item>`_ endpoint.

        Response format is determined by `flags <https://help.wialon.com/en/api/user-guide/data-format>`_.

        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param flags: ``core/search_item`` Wialon API response flags. Default is ``0x1``.
        :type flags: int
        :returns: A dictionary of Wialon object data.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, typing.Any] = {}
        params["id"] = self.id
        params["flags"] = flags
        return session.wialon_api.core_search_item(**params)
