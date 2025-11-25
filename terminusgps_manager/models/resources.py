from django.db import models
from django.utils.translation import gettext_lazy as _

from terminusgps_manager.models.base import WialonObject


class WialonResource(WialonObject):
    """A Wialon resource."""

    is_account = models.BooleanField(
        default=False, help_text=_("Whether the resource is an account.")
    )
    """Whether the resource is an account."""

    class Meta:
        verbose_name = _("wialon resource")
        verbose_name_plural = _("wialon resources")
