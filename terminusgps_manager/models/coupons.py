import decimal
import uuid

from django.db import models


class Coupon(models.Model):
    name = models.CharField(max_length=128)
    code = models.UUIDField(default=uuid.uuid4)
    trial_occurrences = models.IntegerField(default=1)
    trial_amount = models.DecimalField(
        default=decimal.Decimal("0.00"), max_digits=9, decimal_places=2
    )
    issued_on = models.DateTimeField(auto_now=True)
    redeemed_on = models.DateTimeField(default=None, null=True, blank=True)
    expires_on = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self) -> str:
        """Returns the coupon name."""
        return self.name
