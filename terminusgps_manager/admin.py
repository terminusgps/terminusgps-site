from django.contrib import admin

from . import models


@admin.register(models.TerminusGPSCustomer)
class TerminusGPSCustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(models.WialonAccount)
class WialonAccountAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.WialonUser)
class WialonUserAdmin(admin.ModelAdmin):
    list_display = ["name"]
