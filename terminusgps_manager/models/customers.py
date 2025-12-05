from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _


class TerminusgpsCustomer(models.Model):
    """A Terminus GPS customer."""

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="terminusgps_customer",
    )
    """Django user."""
    account = models.ForeignKey(
        "terminusgps_manager.WialonResource",
        blank=True,
        default=None,
        null=True,
        on_delete=models.CASCADE,
        related_name="wialon_account",
    )
    """Associated Wialon account."""
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
        return str(self.user)
