from django.contrib import admin, messages
from django.utils.translation import ngettext

from terminusgps_tracker.models import (
    Customer,
    CustomerAsset,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerSubscription,
    SubscriptionFeature,
    SubscriptionTier,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "user"]
    actions = [
        "refresh_customer_payment_methods",
        "refresh_customer_shipping_addresses",
    ]
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

    @admin.action(description="Refresh selected customers payment methods")
    def refresh_customer_payment_methods(self, request, queryset):
        [customer.authorizenet_sync_payment_profiles() for customer in queryset]
        self.message_user(
            request,
            ngettext(
                "Refreshed %(count)s customer payment methods.",
                "Refreshed %(count)s customers payment methods.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )

    @admin.action(description="Refresh selected customers shipping addresses")
    def refresh_customer_shipping_addresses(self, request, queryset):
        [customer.authorizenet_sync_address_profiles() for customer in queryset]
        self.message_user(
            request,
            ngettext(
                "Refreshed %(count)s customer shipping addresses.",
                "Refreshed %(count)s customers shipping addresses.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(CustomerAsset)
class CustomerAssetAdmin(admin.ModelAdmin):
    list_display = ["customer"]


@admin.register(CustomerPaymentMethod)
class CustomerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer"]
    view_on_site = False


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer"]
    view_on_site = False


@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer", "status"]
    readonly_fields = ["status", "payment", "address"]


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]


@admin.register(SubscriptionFeature)
class SubscriptionFeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]
