from django.contrib import admin, messages
from django.utils.translation import ngettext

from terminusgps_tracker.models.customers import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerWialonUnit,
)
from terminusgps_tracker.models.subscriptions import (
    Subscription,
    SubscriptionFeature,
    SubscriptionTier,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "authorizenet_profile_id", "user"]
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


@admin.register(CustomerWialonUnit)
class CustomerWialonUnitAdmin(admin.ModelAdmin):
    list_display = ["name", "imei", "id"]
    actions = ["wialon_sync"]

    @admin.action(description="Sync selected unit data with Wialon")
    def wialon_sync(self, request, queryset):
        for unit in queryset:
            unit.wialon_sync()
            unit.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s unit had its data synced with Wialon.",
                "%(count)s units had their data synced with Wialon.",
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
    actions = ["authorizenet_sync"]

    @admin.action(description="Sync selected subscriptions with Authorizenet")
    def authorizenet_sync(self, request, queryset):
        for sub in queryset:
            sub.authorizenet_sync()
            sub.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s subscription was synced with Authorizenet.",
                "%(count)s subscriptions were synced with Authorizenet.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(SubscriptionTier)
class SubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]


@admin.register(SubscriptionFeature)
class SubscriptionFeatureAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "desc"]
