from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class WialonUnit(models.Model):
    """A Wialon unit."""

    wialon_id = models.PositiveIntegerField()
    """
    Unit Wialon ID.

    :type: int

    """
    name = models.CharField(max_length=50, validators=[MinLengthValidator(4)])
    """
    Unit name.

    :type: str

    """

    class Meta:
        ordering = ["name"]
        verbose_name = _("wialon unit")
        verbose_name_plural = _("wialon units")

    def __str__(self) -> str:
        """Returns the unit name."""
        return self.name
