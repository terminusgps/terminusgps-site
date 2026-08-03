from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from terminusgps.wialon import (
    generate_locator_token,
    generate_locator_url,
    get_resources,
    get_session,
    get_unit_by_imei,
)


class InstallJobStatus(models.TextChoices):
    NEEDS_BILLING = "needs_billing", _("Needs billing")
    DONE = "done", _("Done")


class InstallJobQuerySet(models.QuerySet):
    def all_not_done_jobs(self):
        return self.exclude(status=InstallJobStatus.DONE)


class EmployeeQuerySet(models.QuerySet):
    def get_by_user(self, user: AbstractBaseUser):
        try:
            obj = self.get(user=user)
        except self.model.DoesNotExist:
            return None
        else:
            return obj


class WialonResourceQuerySet(models.QuerySet):
    def sync_from_wialon(self, sid: str | None = None):
        session = get_session(sid=sid)
        resources = get_resources(session)
        new_resources = [
            WialonResource(id=resource["id"], name=resource["nm"])
            for resource in resources
        ]
        self.bulk_create(new_resources, ignore_conflicts=True)
        return self.filter()


class WialonUnitQuerySet(models.QuerySet):
    def with_wialon_commands(self, sid: str | None = None) -> list:
        unit_qs = self.filter()
        commands = [unit._get_wialon_commands(sid=sid) for unit in unit_qs]
        return list(zip(unit_qs, commands))


class Employee(models.Model):
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name="employee"
    )
    objects = EmployeeQuerySet.as_manager()

    class Meta:
        verbose_name = _("employee")
        verbose_name_plural = _("employees")

    def __str__(self) -> str:
        return str(self.user)


class WialonResource(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    objects = WialonResourceQuerySet.as_manager()

    class Meta:
        verbose_name = _("wialon resource")
        verbose_name_plural = _("wialon resources")

    def __str__(self) -> str:
        return self.name


class WialonUnit(models.Model):
    job = models.ForeignKey(
        "terminusgps_installer.InstallJob",
        on_delete=models.CASCADE,
        related_name="units",
    )
    name = models.CharField(blank=True, max_length=50)
    imei = models.CharField(max_length=20)
    vin = models.CharField(blank=True, max_length=17)
    plate = models.CharField(blank=True, max_length=12)
    mileage = models.PositiveIntegerField(blank=True, default=0)
    locator_url = models.URLField(blank=True)
    objects = WialonUnitQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name if self.name else f"WialonUnit #{self.pk}"

    def get_wialon_unit_name_and_save(self, sid: str | None = None) -> str:
        self.name = self._get_wialon_unit_name(sid)
        self.save(update_fields=["name"])
        return self.name

    def refresh_locator_url_and_save(self, sid: str | None = None) -> str:
        session = get_session(sid=sid)
        unit = get_unit_by_imei(session, self.imei)
        token = generate_locator_token(session, [unit["id"]])
        self.locator_url = generate_locator_url(token)
        self.save(update_fields=["locator_url"])
        return self.locator_url

    def _get_wialon_unit_name(self, sid: str | None = None) -> str:
        session = get_session(sid=sid)
        unit = get_unit_by_imei(session, self.imei)
        return unit["nm"]

    def _get_wialon_unit_id(self, sid: str | None = None) -> int:
        session = get_session(sid=sid)
        unit = get_unit_by_imei(session, self.imei)
        return unit["id"]

    def _get_wialon_commands(self, sid: str | None = None) -> list[dict]:
        session = get_session(sid=sid)
        unit = get_unit_by_imei(session, self.imei, flags=512)
        return unit["cmds"]


class InstallJob(models.Model):
    company = models.ForeignKey(
        "terminusgps_installer.WialonResource",
        help_text=_("Select a company."),
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    employee = models.ForeignKey(
        "terminusgps_installer.Employee",
        help_text=_("Select an employee responsible for this job."),
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
