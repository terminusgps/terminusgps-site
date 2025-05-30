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
        for job_obj in queryset:
            if job_obj.completed:
                results_map["skipped"].append(job_obj)
                continue
            job_obj.completed = True
            results_map["success"].append(job_obj)

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
        for job_obj in queryset:
            if not job_obj.completed:
                results_map["skipped"].append(job_obj)
                continue
            job_obj.completed = False
            results_map["success"].append(job_obj)

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
    list_display = ["name", "id"]
    ordering = ["name"]
    actions = ["wialon_sync_accounts"]

    @admin.action(description="Sync selected account data with Wialon")
    def wialon_sync_accounts(self, request, queryset):
        with WialonSession() as session:
            for account_obj in queryset:
                account_obj.wialon_sync(session)
                account_obj.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s account was synced using the Wialon API.",
                "%(count)s accounts were synced using the Wialon API.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(WialonAsset)
class WialonAssetAdmin(admin.ModelAdmin):
    list_display = ["name", "id", "imei"]
    ordering = ["name"]
    actions = ["wialon_sync_assets"]

    @admin.action(description="Sync selected asset data with Wialon")
    def wialon_sync_assets(self, request, queryset):
        with WialonSession() as session:
            for asset_obj in queryset:
                asset_obj.wialon_sync(session)
                asset_obj.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s asset was synced using the Wialon API.",
                "%(count)s assets were synced using the Wialon API.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(WialonAssetCommand)
class WialonAssetCommandAdmin(admin.ModelAdmin):
    list_display = ["name", "asset", "cmd_type"]
    list_filter = ["asset", "cmd_type"]
    ordering = ["name"]
    actions = ["wialon_sync_commands", "wialon_execute_commands"]

    @admin.action(description="Sync selected command data with Wialon")
    def wialon_sync_commands(self, request, queryset):
        with WialonSession() as session:
            for cmd_obj in queryset:
                cmd_obj.wialon_sync(session)
                cmd_obj.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s command was synced using the Wialon API.",
                "%(count)s commands were synced using the Wialon API.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )

    @admin.action(description="Execute selected commands with Wialon")
    def wialon_execute_commands(self, request, queryset):
        with WialonSession() as session:
            for cmd_obj in queryset:
                cmd_obj.execute(session)

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
