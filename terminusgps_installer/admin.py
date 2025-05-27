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
    list_display = ["date_created", "installer"]


@admin.register(WialonAccount)
class WialonAccountAdmin(admin.ModelAdmin):
    list_display = ["name"]
    ordering = ["name"]


@admin.register(WialonAsset)
class WialonAssetAdmin(admin.ModelAdmin):
    list_display = ["name"]
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
    list_filter = ["name", "asset"]
    ordering = ["name"]
