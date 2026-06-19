from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import validate_imei


class InstallJobStatus(models.TextChoices):
    STARTED = "started", _("Started")
    NEEDS_BILLING = "needs_billing", _("Needs billing")
    COMPLETE = "complete", _("Complete")


class InstallJobQuerySet(models.QuerySet):
    def all_incomplete_jobs(self):
        return self.exclude(status=InstallJobStatus.COMPLETE)


class Installer(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="installer"
    )

    class Meta:
        verbose_name = _("installer")
        verbose_name_plural = _("installers")

    def __str__(self) -> str:
        return str(self.user)


class InstallJob(models.Model):
    installer = models.ForeignKey(
        "terminusgps_installer.Installer",
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    status = models.CharField(
        choices=InstallJobStatus.choices, default=InstallJobStatus.STARTED
    )
    resource = models.CharField(
        validators=[MinLengthValidator(8), MaxLengthValidator(8)]
    )
    imei = models.CharField(validators=[MinLengthValidator(15), validate_imei])
    vin = models.CharField(
        blank=True, validators=[MinLengthValidator(17), MaxLengthValidator(17)]
    )
    crt_date = models.DateTimeField(auto_now_add=True)
    mod_date = models.DateTimeField(auto_now=True)
    objects = InstallJobQuerySet.as_manager()

    class Meta:
        verbose_name = _("install job")
        verbose_name_plural = _("install jobs")

    def __str__(self) -> str:
        return f"InstallJob #{self.pk}"
