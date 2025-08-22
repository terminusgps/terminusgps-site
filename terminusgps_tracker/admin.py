from django.contrib import admin

from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerSubscription,
    CustomerSubscriptionTier,
    CustomerWialonUnit,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    actions = ["sync_with_authorizenet", "sync_with_wialon"]
    list_display = [
        "id",
        "user",
        "authorizenet_profile_id",
        "wialon_resource_id",
        "wialon_user_id",
    ]


@admin.register(CustomerWialonUnit)
class CustomerWialonUnitAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]


@admin.register(CustomerPaymentMethod)
class CustomerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]


@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status"]
    list_filter = ["status"]


@admin.register(CustomerSubscriptionTier)
class CustomerSubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "desc"]
