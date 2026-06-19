from django.contrib import admin

from . import models


@admin.register(models.Employee)
class EmployeeModelAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(models.InstallJob)
class InstallJobModelAdmin(admin.ModelAdmin):
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
