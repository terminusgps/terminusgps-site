from django.contrib import admin, messages
from django.utils.translation import ngettext

from terminusgps_tracker.models.customers import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
)
from terminusgps_tracker.models.subscriptions import (
    Subscription,
    SubscriptionFeature,
    SubscriptionTier,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["user"]
    actions = [
        "authorizenet_sync_payment_profiles",
        "authorizenet_sync_address_profiles",
    ]

    @admin.action(
        description="Sync selected customer payment profiles with Authorizenet"
    )
    def authorizenet_sync_payment_profiles(self, request, queryset):
        for customer in queryset:
            customer.authorizenet_sync_payment_profiles()

        self.message_user(
            request,
            ngettext(
                "%(count)s customer had its payment profiles synced with Authorizenet.",
                "%(count)s customers had their payment profiles synced with Authorizenet.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )

    @admin.action(
        description="Sync selected customer address profiles with Authorizenet"
    )
    def authorizenet_sync_address_profiles(self, request, queryset):
        for customer in queryset:
            customer.authorizenet_sync_address_profiles()

        self.message_user(
            request,
            ngettext(
                "%(count)s customer had its address profiles synced with Authorizenet.",
                "%(count)s customers had their address profiles synced with Authorizenet.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(CustomerPaymentMethod)
class CustomerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]
    list_filter = ["customer"]
    view_on_site = False


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]
    list_filter = ["customer"]
    view_on_site = False


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["customer", "status"]
    list_filter = ["status"]
    readonly_fields = ["status"]


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]


@admin.register(SubscriptionFeature)
class SubscriptionFeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]
