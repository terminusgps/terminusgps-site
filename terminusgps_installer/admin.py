from django.contrib import admin

from . import models


@admin.register(models.Installer)
class InstallerModelAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(models.InstallJob)
class InstallJobModelAdmin(admin.ModelAdmin):
    list_display = ["installer", "imei", "status", "crt_date", "mod_date"]
    date_hierarchy = "crt_date"
    list_filter = ["status"]
