from django.contrib import admin

from . import models


@admin.register(models.TerminusgpsCustomer)
class TerminusgpsCustomerAdmin(admin.ModelAdmin):
    readonly_fields = ["tax", "grand_total"]
    exclude = ["subscription"]
    fieldsets = [
        (None, {"fields": ["user", "account"]}),
        (
            "Pricing",
            {"fields": ["tax_rate", "subtotal", "tax", "grand_total"]},
        ),
    ]


@admin.register(models.WialonResource)
class WialonResourceAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]


@admin.register(models.WialonUnit)
class WialonUnitAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]


@admin.register(models.WialonUser)
class WialonUserAdmin(admin.ModelAdmin):
    list_display = ["name", "id"]
