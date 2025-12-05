from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class WialonResource(models.Model):
    """A Wialon resource."""

    creator_id = models.PositiveIntegerField()
    """
    Resource creator user ID.

    :type: int

    """
    wialon_id = models.PositiveIntegerField()
    """
    Resource Wialon ID.

    :type: int

    """
    name = models.CharField(max_length=50, validators=[MinLengthValidator(4)])
    """
    Resource name.

    :type: str

    """

    class Meta:
        ordering = ["name"]
        verbose_name = _("wialon resource")
        verbose_name_plural = _("wialon resources")

    def __str__(self) -> str:
        """Returns the resource name."""
        return self.name
