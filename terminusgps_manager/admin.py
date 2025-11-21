from django.contrib import admin

from . import models


@admin.register(models.TerminusgpsCustomer)
class TerminusgpsCustomerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WialonResource)
class WialonResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WialonUnit)
class WialonUnitAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WialonUser)
class WialonUserAdmin(admin.ModelAdmin):
    pass
