from django.contrib import admin, messages
from django.utils.translation import ngettext
from terminusgps.wialon.session import WialonSession

from .models import (
    Installer,
    InstallJob,
    WialonAccount,
    WialonAsset,
    WialonAssetCommand,
)


@admin.register(Installer)
class InstallerAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(InstallJob)
class InstallJobAdmin(admin.ModelAdmin):
    list_display = ["asset", "installer", "date_created", "completed"]
    list_filter = ["installer", "date_created", "completed"]
    actions = ["complete_jobs", "uncomplete_jobs"]

    @admin.action(description="Set selected jobs as completed")
    def complete_jobs(self, request, queryset):
        results_map = {"skipped": [], "success": []}

        for job in queryset:
            if job.completed:
                results_map["skipped"].append(job)
                continue
            job.completed = True
            results_map["success"].append(job)

        if results_map["skipped"]:
            self.message_user(
                request,
                ngettext(
                    "%(count)s job was already complete and was skipped.",
                    "%(count)s jobs were already complete and were skipped.",
                    len(results_map["skipped"]),
                )
                % {"count": len(results_map["skipped"])},
                messages.WARNING,
            )

        if results_map["success"]:
            InstallJob.objects.bulk_update(results_map["success"], fields=["completed"])
            self.message_user(
                request,
                ngettext(
                    "%(count)s job was set as complete.",
                    "%(count)s jobs were set as complete.",
                    len(results_map["success"]),
                )
                % {"count": len(results_map["success"])},
                messages.SUCCESS,
            )

    @admin.action(description="Set selected jobs as not completed")
    def uncomplete_jobs(self, request, queryset):
        results_map = {"skipped": [], "success": []}

        for job in queryset:
            if not job.completed:
                results_map["skipped"].append(job)
                continue
            job.completed = False
            results_map["success"].append(job)

        if results_map["skipped"]:
            self.message_user(
                request,
                ngettext(
                    "%(count)s job was already not complete and was skipped.",
                    "%(count)s jobs were already not complete and were skipped.",
                    len(results_map["skipped"]),
                )
                % {"count": len(results_map["skipped"])},
                messages.WARNING,
            )

        if results_map["success"]:
            InstallJob.objects.bulk_update(results_map["success"], fields=["completed"])
            self.message_user(
                request,
                ngettext(
                    "%(count)s job was set as not complete.",
                    "%(count)s jobs were set as not complete.",
                    len(results_map["success"]),
                )
                % {"count": len(results_map["success"])},
                messages.SUCCESS,
            )


@admin.register(WialonAccount)
class WialonAccountAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


@admin.register(WialonAsset)
class WialonAssetAdmin(admin.ModelAdmin):
    list_display = ["name", "imei"]
    ordering = ["name"]
    actions = ["wialon_sync_commands"]

    @admin.action(description="Sync commands for selected assets")
    def wialon_sync_commands(self, request, queryset):
        with WialonSession() as session:
            for asset in queryset:
                asset.save(session)

        self.message_user(
            request,
            ngettext(
                "%(count)s asset had its commands synced with Wialon.",
                "%(count)s assets had their commands synced with Wialon.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(WialonAssetCommand)
class WialonAssetCommandAdmin(admin.ModelAdmin):
    list_display = ["name", "asset"]
    list_filter = ["asset"]
    ordering = ["name"]
    actions = ["wialon_sync", "wialon_execute"]

    @admin.action(description="Execute selected commands in Wialon")
    def wialon_execute(self, request, queryset):
        with WialonSession() as session:
            for cmd in queryset:
                cmd.execute(session)

        self.message_user(
            request,
            ngettext(
                "%(count)s command was executed.",
                "%(count)s commands were executed.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )

    @admin.action(description="Sync selected command data with Wialon")
    def wialon_sync(self, request, queryset):
        with WialonSession() as session:
            for cmd in queryset:
                cmd.save(session)

        self.message_user(
            request,
            ngettext(
                "%(count)s command had its data synced with Wialon.",
                "%(count)s commands had their data synced with Wialon.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )
