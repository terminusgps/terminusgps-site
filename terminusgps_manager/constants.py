from django.db import models
from django.utils.translation import gettext_lazy as _


class WialonUserMeasurementType(models.IntegerChoices):
    SI = 0, _("SI")
    US = 1, _("US")
    IMPERIAL = 3, _("Imperial")
    METRIC_GALLONS = 4, _("Metric w/ gallons")
