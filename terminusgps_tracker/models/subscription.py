from django.db import models
from django.utils.translation import gettext_lazy as _


class TerminusSubscription(models.Model):
    class TerminusSubscriptionTier(models.TextChoices):
        COPPER = "Cu", _("Copper")
        SILVER = "Ag", _("Silver")
        GOLD = "Au", _("Gold")
        PLATINUM = "Pt", _("Platinum")

    name = models.CharField(max_length=64)
    profile = models.ForeignKey(
        "CustomerProfile", on_delete=models.CASCADE, related_name="subscriptions"
    )
    tier = models.CharField(
        max_length=2,
        choices=TerminusSubscriptionTier.choices,
        default=TerminusSubscriptionTier.COPPER,
    )

    def __str__(self) -> str:
        return self.name
