from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class WialonUser(models.Model):
    """A Wialon user."""

    creator_id = models.PositiveIntegerField(default=settings.WIALON_ADMIN_ID)
    """
    User creator user ID.

    :type: int

    """
    wialon_id = models.PositiveIntegerField()
    """
    User Wialon ID.

    :type: int

    """
    name = models.CharField(max_length=50, validators=[MinLengthValidator(4)])
    """
    User name.

    :type: str

    """

    class Meta:
        ordering = ["name"]
        verbose_name = _("wialon user")
        verbose_name_plural = _("wialon users")

    def __str__(self) -> str:
        """Returns the user name."""
        return self.name
