from functools import cached_property

from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from terminusgps.wialon import get_session, get_unit_by_imei

from .validators import validate_imei, validate_vin


class InstallJobStatus(models.TextChoices):
    NEEDS_BILLING = "needs_billing", _("Needs billing")
    DONE = "done", _("Done")


class InstallJobQuerySet(models.QuerySet):
    def all_not_done_jobs(self):
        return self.exclude(status=InstallJobStatus.DONE)


class Employee(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="employee"
    )

    class Meta:
        verbose_name = _("employee")
        verbose_name_plural = _("employees")

    def __str__(self) -> str:
        return str(self.user)


class InstallJob(models.Model):
    imei = models.CharField(
        help_text=_(
            "Provide the 15-digit IMEI number present on the tracking device. Ex: 869738060092801"
        ),
        unique=True,
        validators=[
            MinLengthValidator(15),
            MaxLengthValidator(15),
            validate_imei,
        ],
    )
    resource = models.CharField(
        help_text=_("Select a Wialon resource from the list."),
        validators=[MinLengthValidator(8), MaxLengthValidator(8)],
    )
    vin = models.CharField(
        blank=True,
        help_text=_(
            "Optional. Provide the vehicle's 17-character VIN number. Ex: JTHBA30G065155212"
        ),
        validators=[
            MinLengthValidator(17),
            MaxLengthValidator(17),
            validate_vin,
        ],
    )

    employee = models.ForeignKey(
        "terminusgps_installer.Employee",
        help_text=_("Select the employee responsible for this job."),
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    status = models.CharField(
        choices=InstallJobStatus.choices,
        default=InstallJobStatus.NEEDS_BILLING,
    )
    crt_date = models.DateTimeField(auto_now_add=True)
    mod_date = models.DateTimeField(auto_now=True)

    objects = InstallJobQuerySet.as_manager()

    class Meta:
        get_latest_by = "crt_date"
        ordering = ["crt_date"]
        verbose_name = _("install job")
        verbose_name_plural = _("install jobs")

    def __str__(self) -> str:
        return f"InstallJob #{self.pk}"

    def get_absolute_url(self) -> str:
        return reverse("installer:job details", kwargs={"job_pk": self.pk})


class WialonMap(models.Model):
    sid = models.CharField(blank=True)
    job = models.ForeignKey(
        "terminusgps_installer.InstallJob",
        on_delete=models.CASCADE,
        related_name="maps",
    )

    def __str__(self) -> str:
        return f"Job #{self.job.pk} Map Renderer"

    @property
    def is_active(self) -> bool:
        session = get_session(sid=self.sid)
        return session.id == self.sid

    @cached_property
    def unit_id(self) -> int:
        session = get_session(sid=self.sid)
        if not self.is_active:
            self.sid = session.id
            self.save(update_fields=["sid"])
        unit = get_unit_by_imei(session, self.job.imei)
        return unit["id"]
