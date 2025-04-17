from django.contrib import admin

from terminusgps_install.models import Installer, WialonAccount, WialonAsset


@admin.register(Installer)
class InstallerAdmin(admin.ModelAdmin):
    list_display = ["wialon_id", "user"]


@admin.register(WialonAccount)
class WialonAccountAdmin(admin.ModelAdmin):
    list_display = ["wialon_id", "name"]


@admin.register(WialonAsset)
class WialonAssetAdmin(admin.ModelAdmin):
    list_display = ["wialon_id", "name", "account"]
