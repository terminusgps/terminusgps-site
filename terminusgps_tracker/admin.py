from django.contrib import admin

from terminusgps_tracker.models import (
    Customer,
    CustomerWialonUnit,
    SubscriptionTier,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user", "subscription"]


@admin.register(CustomerWialonUnit)
class CustomerWialonUnitAdmin(admin.ModelAdmin):
    list_display = ["name", "tier", "customer"]
    list_filter = ["tier"]


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]
