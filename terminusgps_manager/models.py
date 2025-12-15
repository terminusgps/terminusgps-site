import decimal
import typing

from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.session import WialonSession


class TerminusgpsCustomer(models.Model):
    """A Terminus GPS customer."""

    django_user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="terminusgps_customer",
    )
    """Django user."""
    wialon_user = models.ForeignKey(
        "terminusgps_manager.WialonUser",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        default=None,
    )
    """Wialon user."""
    tax_rate = models.DecimalField(
        decimal_places=4,
        default=0.0825,
        help_text="Enter a tax rate as a decimal.",
        max_digits=9,
    )
    """Tax rate."""
    subtotal = models.DecimalField(
        decimal_places=2,
        default=24.99,
        help_text="Enter an amount to charge the customer every payment period.",
        max_digits=9,
    )
    """Subtotal."""
    tax = models.GeneratedField(
        db_persist=True,
        expression=(F("subtotal") * (F("tax_rate") + 1)) - F("subtotal"),
        help_text="Automatically generated tax amount.",
        output_field=models.DecimalField(max_digits=9, decimal_places=2),
    )
    """Tax total."""
    grand_total = models.GeneratedField(
        db_persist=True,
        expression=F("subtotal") * (F("tax_rate") + 1),
        help_text="Automatically generated grand total amount (subtotal+tax).",
        output_field=models.DecimalField(max_digits=9, decimal_places=2),
    )
    """Grand total (subtotal + tax)."""
    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        blank=True,
        default=None,
        null=True,
        on_delete=models.SET_NULL,
        related_name="terminusgps_customer",
    )
    """Subscription."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        """Returns the customer's username."""
        return str(self.django_user)


class WialonUser(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    """
    Wialon user ID.

    :type: int

    """
    name = models.CharField(max_length=50, validators=[MinLengthValidator(4)])
    """
    Wialon user name.

    :type: str

    """

    def __str__(self) -> str:
        """Returns the Wialon user name."""
        return self.name

    def set_access(
        self, id: int, mask: int, *, session: WialonSession
    ) -> None:
        """
        Sets user access rights on the other Wialon object.

        :param id: A Wialon object ID.
        :type id: int
        :param mask: An access rights mask.
        :type mask: int
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int] = {}
        params["userId"] = self.id
        params["itemId"] = id
        params["accessMask"] = mask
        session.wialon_api.user_update_item_access(**params)
        return

    def set_password(
        self, old: str, new: str, *, session: WialonSession
    ) -> None:
        """
        Sets the user's password to ``new``.

        :param old: The Wialon user's original password.
        :type old: str
        :param new: The Wialon user's new password.
        :type new: str
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int | str] = {}
        params["userId"] = self.id
        params["oldPassword"] = old
        params["newPassword"] = new
        session.wialon_api.user_update_password(**params)
        return


class WialonUnit(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    """
    Wialon unit ID.

    :type: int

    """
    name = models.CharField(max_length=50, validators=[MinLengthValidator(4)])
    """
    Wialon unit name.

    :type: str

    """

    def __str__(self) -> str:
        """Returns the Wialon unit name."""
        return self.name


class WialonAccount(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    """
    Wialon account ID.

    :type: int

    """
    name = models.CharField(max_length=50, validators=[MinLengthValidator(4)])
    """
    Wialon account name.

    :type: str

    """

    def __str__(self) -> str:
        """Returns the Wialon account name."""
        return self.name

    def migrate(self, id: int, *, session: WialonSession) -> None:
        """
        Migrates a Wialon object into the account by id.

        :param id: A Wialon object ID.
        :type id: int
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :raises ValueError: If something went wrong during a Wialon API call.
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int] = {}
        params["itemId"] = id
        params["resourceId"] = self.id
        session.wialon_api.account_change_account(**params)
        return

    def enable(self, *, session: WialonSession) -> None:
        """
        Enables the account in Wialon.

        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int] = {}
        params["itemId"] = self.id
        params["enable"] = int(True)
        session.wialon_api.account_enable_account(**params)
        return

    def disable(self, *, session: WialonSession) -> None:
        """
        Disables the account in Wialon.

        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int] = {}
        params["itemId"] = self.id
        params["enable"] = int(False)
        session.wialon_api.account_enable_account(**params)
        return

    def get_data(
        self, flags: typing.Literal[1, 2, 4, 8] = 1, *, session: WialonSession
    ) -> dict[str, typing.Any]:
        """
        Returns account data from Wialon.

        :param flags: `account/get_account_data <https://help.wialon.com/en/api/user-guide/api-reference/account/get_account_data>`_ response flags. Default is ``1``.
        :type flags: ~typing.Literal[1, 2, 4, 8]
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: An account data dictionary.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, int] = {}
        params["itemId"] = self.id
        params["type"] = flags
        return session.wialon_api.account_get_data(**params)

    def get_history(
        self, days: int, timezone: int, *, session: WialonSession
    ) -> dict[str, typing.Any]:
        """
        Returns account history from Wialon.

        :param days: Interval for account history in days.
        :type days: int
        :param timezone: Timezone.
        :type timezone: int
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: An account history dictionary.
        :rtype: dict[str, ~typing.Any]

        """
        params: dict[str, int] = {}
        params["itemId"] = self.id
        params["days"] = days
        params["tz"] = timezone
        return session.wialon_api.account_get_account_history(**params)

    def set_flags(
        self,
        flags: int,
        *,
        block_balance: decimal.Decimal | None = None,
        deny_balance: decimal.Decimal | None = None,
        session: WialonSession,
    ) -> None:
        """
        Sets account flags in Wialon.

        :param flags: Account settings flags.
        :type flags: int
        :param block_balance: Balance amount at which to block the account. Default is :py:obj:`None`.
        :type block_balance: ~decimal.Decimal | None
        :param deny_balance: Balance amount at which to deny access to paid services. Default is :py:obj:`None`.
        :type deny_balance: ~decimal.Decimal | None
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int | decimal.Decimal] = {}
        params["itemId"] = self.id
        params["flags"] = flags
        if block_balance is not None:
            params["blockBalance"] = block_balance
        if deny_balance is not None:
            params["denyBalance"] = deny_balance
        session.wialon_api.account_update_flags(**params)
        return

    def set_min_days(self, days: int, *, session: WialonSession) -> None:
        """
        Sets the account's minimum days in Wialon.

        :param days: Minimum number of days.
        :type days: int
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: :py:obj:`None`

        """
        params: dict[str, int] = {}
        params["itemId"] = self.id
        params["minDays"] = days
        session.wialon_api.account_update_min_days(**params)
        return

    def set_plan(self, plan: str, *, session: WialonSession) -> None:
        """
        Sets the account billing plan in Wialon.

        :param plan: A billing plan.
        :type plan: str
        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :returns: Nothing.
        :rtype: None

        """
        params: dict[str, int | str] = {}
        params["itemId"] = self.id
        params["plan"] = plan
        session.wialon_api.account_update_plan(**params)
        return

    def make_payment(
        self,
        amount: decimal.Decimal | None = None,
        *,
        days: int | None = None,
        desc: str | None = None,
        session: WialonSession,
    ) -> None:
        """
        Makes a payment in Wialon.

        Either ``amount`` or ``days`` must be provided.

        :param session: A valid Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param amount: Amount to update the account balance by. May be negative. Default is :py:obj:`None`.
        :type amount: ~decimal.Decimal | None
        :param days: Number of days to add to the account. May be negative. Default is :py:obj:`None`.
        :type days: int | None
        :param desc: Payment description. Default is :py:obj:`None`.
        :type desc: str | None
        :raises ValueError: If neither ``amount`` nor ``days`` were provided.
        :returns: Nothing.
        :rtype: None

        """
        if all([amount is None, days is None]):
            raise ValueError("'amount' or 'days' is required, got neither.")
        params: dict[str, int | str | decimal.Decimal] = {}
        params["itemId"] = self.id
        if amount is not None:
            params["balanceUpdate"] = amount
        if days is not None:
            params["daysUpdate"] = days
        if desc is not None:
            params["description"] = desc
        session.wialon_api.account_do_payment(**params)
        return
