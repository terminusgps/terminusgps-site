import decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _


class TerminusGPSCustomer(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
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

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        return str(self.user)
