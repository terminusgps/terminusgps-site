import typing
from collections.abc import Sequence

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.session import WialonSession


class TerminusgpsCustomer(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="terminusgps_customer",
    )

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        return str(self.user)


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
        Returns a dictionary of data for the Wialon object.

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


class WialonResource(WialonObject):
    is_account = models.BooleanField(default=False)
    """Whether the resource is an account."""

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")


class WialonUnit(WialonObject):
    class Meta:
        verbose_name = _("unit")
        verbose_name_plural = _("units")

    def get_command_data(
        self,
        session: WialonSession,
        *,
        command_ids: Sequence[int] | None = None,
    ) -> dict[str, typing.Any]:
        """
        Returns all commands for the unit.

        If :py:attr:`command_ids` is provided, returns all commands specified.

        :param session: Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param command_ids: Sequence of command ids. Default is :py:obj:`None`.
        :type command_ids: ~collections.abc.Sequence[int] | None
        :returns: A dictionary of command definition data.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, typing.Any] = {}
        params["itemId"] = self.id
        if command_ids is not None:
            params["col"] = command_ids
        return session.wialon_api.unit_get_command_definition_data(**params)

    def execute_command(
        self,
        session: WialonSession,
        *,
        command_name: str,
        link_type: str = "vrt",
        timeout: int = 300,
        flags: int = 0,
        extra_params: str | None = None,
    ) -> dict[str, typing.Any]:
        """
        Executes a command for the unit by name.

        :param session: Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param command_name: Command name.
        :type command_name: str
        :param link_type: Command link type. Default is ``"vrt"``.
        :type link_type: str
        :param timeout: Command queue timeout in seconds. Default is ``300``.
        :type timeout: int
        :param flags: Flags for selecting a phone number to execute the command. Default is ``0`` (primary, then secondary).
        :type flags: int
        :param extra_params: Extra command parameters. Default is :py:obj:`None`.
        :type extra_params: str | None

        """
        params: dict[str, typing.Any] = {}
        params["itemId"] = self.id
        params["commandName"] = command_name
        params["linkType"] = link_type
        params["timeout"] = timeout
        params["flags"] = flags
        if extra_params is not None:
            params["param"] = extra_params
        return session.wialon_api.unit_exec_cmd(**params)

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


class WialonUser(WialonObject):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

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
