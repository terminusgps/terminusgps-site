from django.contrib import admin

from terminusgps_tracker.models import (
    Customer,
    CustomerAsset,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    Subscription,
    SubscriptionFeature,
    SubscriptionTier,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "user"]
    fieldsets = [
        (None, {"fields": ["user"]}),
        ("Authorizenet", {"fields": ["authorizenet_id"]}),
        (
            "Wialon",
            {
                "fields": [
                    "wialon_user_id",
                    "wialon_group_id",
                    "wialon_resource_id",
                    "wialon_super_user_id",
                ]
            },
        ),
    ]


@admin.register(CustomerAsset)
class CustomerAssetAdmin(admin.ModelAdmin):
    list_display = ["customer"]


@admin.register(CustomerPaymentMethod)
class CustomerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer"]


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer", "status"]
    readonly_fields = ["status"]


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]


@admin.register(SubscriptionFeature)
class SubscriptionFeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]
