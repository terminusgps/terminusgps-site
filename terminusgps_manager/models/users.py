import typing

from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.session import WialonSession

from terminusgps_manager.models.base import WialonObject


class WialonUser(WialonObject):
    """A Wialon user."""

    class Meta:
        verbose_name = _("wialon user")
        verbose_name_plural = _("wialon users")

    def get_items_by_access(
        self, session: WialonSession, *, items_type: str, required_access: int
    ) -> dict[str, typing.Any]:
        """
        Returns all Wialon objects of the specified :py:attr:`items_type` to which the user has at least the specified required access level.

        :param session: Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param items_type: Wialon object type.
        :type items_type: str
        :param required_access: Required access rights.
        :type required_access: int
        :returns: A dictionary of Wialon object ids.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, typing.Any] = {}
        params["userId"] = self.id
        params["itemSuperclass"] = items_type
        params["reqAccess"] = required_access
        return session.wialon_api.user_get_items_by_access(**params)

    def get_items_access(
        self,
        session: WialonSession,
        *,
        items_type: str,
        direct: bool = False,
        flags: int = 0x1,
    ) -> dict[str, typing.Any]:
        """
        Returns the current access rights the user has to Wialon objects of the specified type.

        :param session: Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param items_type: Wialon object type.
        :type items_type: str
        :param direct: Whether to return only the objects the user has direct access to. Default is :py:obj:`False`.
        :type direct: bool
        :param flags: Response flags. Default is ``0x1``.
        :type flags: int
        :returns: A dictionary of Wialon objects.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, typing.Any] = {}
        params["userId"] = self.id
        params["directAccess"] = str(direct).lower()
        params["itemSuperclass"] = items_type
        params["flags"] = flags
        return session.wialon_api.user_get_items_access(**params)
