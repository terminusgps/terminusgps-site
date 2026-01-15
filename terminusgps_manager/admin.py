from django.contrib import admin

from . import models


@admin.register(models.TerminusGPSCustomer)
class TerminusGPSCustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(models.WialonResource)
class WialonResourceAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.WialonUser)
class WialonUserAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.WialonUnit)
class WialonUnitAdmin(admin.ModelAdmin):
    list_display = ["name"]
