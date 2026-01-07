from django.contrib import admin

from . import models


@admin.register(models.TerminusGPSCustomer)
class TerminusGPSCustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]
