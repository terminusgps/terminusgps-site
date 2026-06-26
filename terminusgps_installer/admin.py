from django.contrib import admin, messages
from django.utils.translation import ngettext

from . import models


@admin.register(models.Employee)
class EmployeeModelAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(models.InstallJobAttachment)
class InstallJobAttachmentModelAdmin(admin.ModelAdmin):
    list_display = ["job", "file", "note"]


@admin.register(models.InstallJob)
class InstallJobModelAdmin(admin.ModelAdmin):
    actions = ["refresh_locator_links"]
    list_display = [
        "employee",
        "imei",
        "resource",
        "status",
        "crt_date",
        "mod_date",
    ]
    date_hierarchy = "crt_date"
    list_filter = ["status"]
    readonly_fields = ["locator_url"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "employee",
                    "imei",
                    "resource",
                    "status",
                    "locator_url",
                ]
            },
        ),
        (
            "Optional",
            {"fields": ["vin", "license_plate", "mileage", "vehicle_id"]},
        ),
    ]

    @admin.action(description="Refresh selected jobs locator URLs")
    def refresh_locator_links(self, request, queryset):
        for job in queryset:
            job.refresh_locator_url()
        self.message_user(
            request,
            ngettext(
                "%d job's locator URL was refreshed.",
                "%d jobs' locator URLs were refreshed.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )
