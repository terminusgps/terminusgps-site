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
