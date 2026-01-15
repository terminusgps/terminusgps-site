import abc
import decimal
import typing
from collections.abc import Sequence

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession
from terminusgps.wialon.utils import generate_wialon_password


class TerminusGPSCustomer(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.PROTECT,
        help_text=_("Select a Django user associated with the customer."),
    )
    """Django user."""
    sub_total = models.DecimalField(
        decimal_places=2,
        default=decimal.Decimal("24.95"),
        help_text=_("Enter a dollar amount to charge the customer monthly."),
        max_digits=9,
    )
    """Customer subtotal."""
    tax_rate = models.DecimalField(
        decimal_places=4,
        default=decimal.Decimal("0.0825"),
        help_text=_("Enter a tax rate to charge the customer sales tax."),
        max_digits=9,
    )
    """Customer effective tax rate."""
    tax_total = models.GeneratedField(
        db_persist=True,
        expression=F("sub_total") * (F("tax_rate") * 1),
        help_text=_(
            "Automatically generated tax amount to collect from the customer."
        ),
        output_field=models.DecimalField(decimal_places=2, max_digits=9),
    )
    """Automatically generated customer tax amount."""
    grand_total = models.GeneratedField(
        db_persist=True,
        expression=F("sub_total") + F("tax_total"),
        help_text=_(
            "Automatically generated total amount (base+tax) to collect from the customer."
        ),
        output_field=models.DecimalField(decimal_places=2, max_digits=9),
    )
    """Automatically generated customer grand total (sub+tax) amount."""
    subscription = models.ForeignKey(
        "terminusgps_payments.Subscription",
        on_delete=models.SET_NULL,
        related_name="terminusgpscustomer",
        default=None,
        blank=True,
        null=True,
    )
    """Associated subscription."""
    wialon_user = models.ForeignKey(
        "terminusgps_manager.WialonUser",
        on_delete=models.SET_NULL,
        related_name="customer",
        blank=True,
        null=True,
        default=None,
    )
    """Associated Wialon user."""
    wialon_resource = models.ForeignKey(
        "terminusgps_manager.WialonResource",
        on_delete=models.SET_NULL,
        related_name="customer",
        blank=True,
        null=True,
        default=None,
    )
    """Associated Wialon resource."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        return str(self.user)


class WialonObject(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(blank=True, max_length=50)
    crt = models.IntegerField(
        blank=True, editable=False, verbose_name=_("creator id")
    )
    bact = models.IntegerField(
        blank=True, editable=False, verbose_name=_("account id")
    )
    uacl = models.IntegerField(
        blank=True, editable=False, verbose_name=_("user access control level")
    )

    class Meta:
        ordering = ["name"]
        abstract = True

    def __str__(self) -> str:
        return self.name if self.name else str(self.pk)

    def save(self, **kwargs) -> None:
        """Syncs the object's local data with Wialon before saving."""
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            if not self.pk:
                self.pk = self.create(session)
            elif kwargs.pop("push", False):
                self.push(session, kwargs.get("update_fields"))
            else:
                self.sync(session)
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the unit in Wialon before deleting it locally."""
        with WialonSession() as session:
            session.wialon_api.item_delete_item(**{"itemId": self.pk})
        return super().delete(*args, **kwargs)

    @abc.abstractmethod
    def create(self, session: WialonSession) -> int:
        raise NotImplementedError("Subclasses must implement this method.")

    def pull(
        self,
        session: WialonSession,
        flags: int = DataFlag.UNIT_BASE | DataFlag.UNIT_BILLING_PROPERTIES,
    ) -> dict[str, typing.Any]:
        """
        Pulls remote object data from Wialon.

        :param session: A Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param flags: `core/search_item` response flags.
        :type flags: int
        :raises WialonAPIError: If something went wrong during a Wialon API call.
        :returns: A dictionary of remote Wialon object data.
        :rtype: dict[str, ~typing.Any]

        """
        return session.wialon_api.core_search_item(
            **{"id": self.pk, "flags": flags}
        )

    def push(
        self,
        session: WialonSession,
        update_fields: Sequence[str] | None = None,
    ) -> None:
        """
        Pushes local object data to Wialon.

        :param session: A Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :param update_fields: A sequence of fields to update in Wialon. Default is :py:obj:`None` (all fields).
        :type update_fields: ~collections.abc.Sequence[str] | None
        :raises WialonAPIError: If something went wrong during a Wialon API call.
        :returns: Nothing.
        :rtype: None

        """
        if update_fields is None or "name" in update_fields:
            session.wialon_api.item_update_name(
                **{"itemId": self.pk, "name": self.name}
            )
        return

    @transaction.atomic
    def sync(self, session: WialonSession) -> None:
        """
        Syncs remote Wialon data with local data.

        :param session: A Wialon API session.
        :type session: ~terminusgps.wialon.session.WialonSession
        :raises WialonAPIError: If something went wrong during a Wialon API call.
        :returns: Nothing.
        :rtype: None

        """
        data = self.pull(session)
        self.name = str(data["item"]["nm"])
        self.uacl = int(data["item"]["uacl"])
        self.crt = int(data["item"]["crt"])
        self.bact = int(data["item"]["bact"])
        return


class WialonUser(WialonObject):
    class Meta:
        verbose_name = _("wialon user")
        verbose_name_plural = _("wialon users")

    @typing.override
    def create(self, session: WialonSession) -> int:
        if not all([self.name, self.crt]):
            raise ValueError("Name and creator id weren't set.")
        resp = session.wialon_api.core_create_user(
            **{
                "creatorId": self.crt,
                "name": self.name,
                "password": generate_wialon_password(),
                "dataFlags": 1,
            }
        )
        return int(resp["item"]["id"])


class WialonUnit(WialonObject):
    imei = models.CharField(blank=True, max_length=64)

    class Meta:
        verbose_name = _("wialon unit")
        verbose_name_plural = _("wialon units")

    @typing.override
    def create(self, session: WialonSession) -> int:
        raise NotImplementedError("Creating Wialon units is not supported.")

    @transaction.atomic
    def sync(self, session: WialonSession) -> None:
        """Syncs remote Wialon data with local data."""
        super().sync(session)
        mask = DataFlag.UNIT_ADVANCED_PROPERTIES
        data = self.pull(session, flags=mask)
        self.imei = str(data["item"]["uid"])
        return


class WialonResource(WialonObject):
    bpact = models.IntegerField(
        blank=True, editable=False, verbose_name=_("parent account id")
    )
    plan = models.CharField(blank=True, default="terminusgps_ext_hist")
    is_account = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("wialon resource")
        verbose_name_plural = _("wialon resources")

    @typing.override
    def delete(self, *args, **kwargs):
        """Deletes the resource/account in Wialon before deleting it locally."""
        with WialonSession() as session:
            if not self.is_account:
                session.wialon_api.item_delete_item(**{"itemId": self.pk})
            else:
                params = {"itemId": self.pk}
                if reasons := kwargs.get("reasons"):
                    params["reasons"] = reasons
                session.wialon_api.account_delete_account(**params)
        return super().delete(*args, **kwargs)

    @typing.override
    def create(self, session: WialonSession) -> int:
        if not all([self.name, self.crt]):
            raise ValueError("Name and/or creator id weren't set.")
        resp = session.wialon_api.core_create_resource(
            **{
                "creatorId": self.crt,
                "name": self.name,
                "skipCreatorCheck": int(True),
                "dataFlags": 1,
            }
        )
        resource_id = int(resp["item"]["id"])
        if self.is_account:
            session.wialon_api.account_create_account(
                **{"itemId": resource_id, "plan": self.plan}
            )
            session.wialon_api.account_enable_account(
                **{"itemId": resource_id, "enable": int(False)}
            )
        return resource_id

    @transaction.atomic
    def sync(self, session: WialonSession) -> None:
        """Syncs remote Wialon data with local data."""
        data = self.pull(session)
        self.bpact = int(data["item"]["bpact"])
        return super().sync(session)

    def migrate(self, session: WialonSession, *, id: int) -> None:
        """Migrates a Wialon object into the account."""
        if not self.is_account:
            raise ValueError(
                f"Can't migrate object #{id}, '{self.name}' isn't an account."
            )
        session.wialon_api.account_change_account(
            **{"resourceId": self.pk, "itemId": id}
        )

    def do_payment(
        self,
        session: WialonSession,
        *,
        bal: decimal.Decimal | None = None,
        days: int | None = None,
        desc: str | None = None,
    ) -> None:
        """Does a payment for the account in Wialon."""
        if not self.is_account:
            raise ValueError(
                f"Can't do payment, '{self.name}' isn't an account."
            )
        if bal is None and days is None:
            raise ValueError(
                "One of 'bal' or 'days' is required, got neither."
            )
        params = {"itemId": self.pk}
        if bal is not None:
            params["balanceUpdate"] = bal
        if days is not None:
            params["daysUpdate"] = days
        if desc is not None:
            params["description"] = desc
        session.wialon_api.account_do_payment(**params)
