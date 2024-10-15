from django.db import models
from django.utils.translation import gettext_lazy as _


class CountryCode(models.TextChoices):
    UNITED_STATES = "US", _("United States")
    CANADA = "CA", _("Canada")
    MEXICO = "MX", _("Mexico")
