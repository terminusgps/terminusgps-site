from django.contrib import admin

from . import models


@admin.register(models.Employee)
class EmployeeModelAdmin(admin.ModelAdmin):
    list_display = ["user"]
    search_fields = ["user__username", "user__email"]


@admin.register(models.WialonUnit)
class WialonUnitAdmin(admin.ModelAdmin):
    list_display = ["imei", "name"]
    search_fields = ["name"]


@admin.register(models.WialonResource)
class WialonResourceAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(models.InstallJob)
class InstallJobModelAdmin(admin.ModelAdmin):
    list_display = ["id", "crt_date", "mod_date"]
    date_hierarchy = "crt_date"
