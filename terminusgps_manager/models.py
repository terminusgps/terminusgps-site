import decimal
import logging
from typing import Literal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonSession

logger = logging.getLogger(__name__)


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
    end_date = models.DateField(blank=True, null=True, default=None)
    """Subscription end date."""

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
        help_text=_("Select a Wialon user from the list."),
    )
    """Associated Wialon user."""
    wialon_account = models.ForeignKey(
        "terminusgps_manager.WialonAccount",
        on_delete=models.SET_NULL,
        related_name="customer",
        blank=True,
        null=True,
        default=None,
        help_text=_("Select a Wialon account from the list."),
    )
    """Associated Wialon resource."""
    wialon_units = models.ManyToManyField(
        "terminusgps_manager.WialonUnit",
        blank=True,
        related_name="customers",
        help_text=_("Select Wialon unit(s) from the list."),
    )
    """Associated Wialon units."""

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        return str(self.user)


class WialonObject(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    name = models.CharField(blank=True, max_length=50)
    crt = models.PositiveIntegerField(
        blank=True, default=None, null=True, verbose_name=_("creator id")
    )
    bact = models.PositiveIntegerField(
        blank=True,
        default=None,
        null=True,
        verbose_name=_("billing account id"),
    )
    uacl = models.PositiveBigIntegerField(
        blank=True,
        default=None,
        null=True,
        verbose_name=_("user access control level"),
    )

    class Meta:
        ordering = ["name"]
        abstract = True

    def __str__(self) -> str:
        return self.name if self.name else str(self.pk)

    def save(self, **kwargs) -> None:
        if kwargs.pop("sync", True):
            logger.debug(f"Syncing #{self.pk} with Wialon...")
            with WialonSession(token=settings.WIALON_TOKEN) as session:
                self.sync(session)
        return super().save(**kwargs)

    def pull(self, session: WialonSession, flags: int = 1) -> dict:
        """Returns remote Wialon object data."""
        return session.wialon_api.core_search_item(
            **{"id": self.pk, "flags": flags}
        )

    @transaction.atomic
    def sync(self, session: WialonSession) -> None:
        """Syncs remote Wialon object data with local database."""
        flags = DataFlag.UNIT_BASE | DataFlag.UNIT_BILLING_PROPERTIES
        data = self.pull(session, flags=flags)
        self.name = str(data["item"]["nm"])
        self.crt = int(data["item"]["crt"])
        self.bact = int(data["item"]["bact"])
        self.uacl = int(data["item"]["uacl"])


class WialonAccount(WialonObject):
    class Meta:
        verbose_name = _("wialon account")
        verbose_name_plural = _("wialon accounts")

    def enable(self, session: WialonSession) -> dict:
        """Enables the account in Wialon."""
        params = {"itemId": self.pk, "enable": int(True)}
        return session.wialon_api.account_enable_account(**params)

    def disable(self, session: WialonSession) -> dict:
        """Disables the account in Wialon."""
        params = {"itemId": self.pk, "enable": int(False)}
        return session.wialon_api.account_enable_account(**params)

    def migrate(self, session: WialonSession, *, id: int) -> dict:
        """Migrates a Wialon object by id into the account."""
        params = {"itemId": id, "resourceId": self.pk}
        return session.wialon_api.account_change_account(**params)

    def get_account_data(
        self, session: WialonSession, response_type: Literal[1, 2, 4, 8] = 1
    ) -> dict:
        """Returns Wialon account data."""
        params = {"itemId": self.pk, "type": response_type}
        return session.wialon_api.account_get_account_data(**params)

    def update_flags(self, session: WialonSession, flags: int) -> dict:
        """Updates account flags in Wialon."""
        params = {"itemId": self.pk, "flags": flags}
        return session.wialon_api.account_update_flags(**params)

    def do_payment(
        self,
        session: WialonSession,
        *,
        bal: decimal.Decimal = decimal.Decimal("0.00"),
        days: int = 0,
        desc: str = "",
    ) -> dict:
        """Does an account payment in Wialon."""
        params = {
            "itemId": self.pk,
            "balanceUpdate": bal,
            "daysUpdate": days,
            "description": desc,
        }
        return session.wialon_api.account_do_payment(**params)


class WialonUnit(WialonObject):
    class Meta:
        verbose_name = _("wialon unit")
        verbose_name_plural = _("wialon units")


class WialonUser(WialonObject):
    class Meta:
        verbose_name = _("wialon user")
        verbose_name_plural = _("wialon users")

    def update_access(
        self, session: WialonSession, *, id: int, access_mask: int
    ) -> dict:
        """Grants Wialon object access to the user."""
        params = {"itemId": id, "userId": self.pk, "accessMask": access_mask}
        return session.wialon_api.user_update_item_access(**params)
