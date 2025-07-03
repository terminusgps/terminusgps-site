from django.contrib import admin, messages
from django.utils.translation import ngettext
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerWialonUnit,
    Subscription,
    SubscriptionFeature,
    SubscriptionTier,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    actions = ["sync_with_authorizenet"]
    list_display = [
        "id",
        "user",
        "authorizenet_profile_id",
        "wialon_resource_id",
        "wialon_user_id",
    ]

    @admin.action(
        description="Sync selected customer payment information with Authorizenet"
    )
    def sync_with_authorizenet(self, request, queryset):
        for customer in queryset:
            customer.authorizenet_sync()
            customer.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s customer had their payment information synced with Authorizenet.",
                "%(count)s customers had their payment information synced with Authorizenet.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )

    @admin.action(
        description="Sync selected customer unit information with Wialon"
    )
    def sync_with_wialon(self, request, queryset):
        with WialonSession() as session:
            for customer in queryset:
                customer.wialon_sync(session)
                customer.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s customer had their unit information synced with Wialon.",
                "%(count)s customers had their unit information synced with Wialon.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(CustomerWialonUnit)
class CustomerWialonUnitAdmin(admin.ModelAdmin):
    actions = ["sync_with_wialon"]
    list_display = ["name", "customer", "imei", "id"]
    list_filter = ["customer"]
    readonly_fields = ["customer"]
    view_on_site = False

    @admin.action(description="Sync selected unit data with Wialon")
    def sync_with_wialon(self, request, queryset):
        with WialonSession() as session:
            for unit in queryset:
                unit.wialon_sync(session)
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
    actions = ["sync_with_authorizenet"]
    list_display = ["id", "customer"]
    list_filter = ["customer"]
    readonly_fields = ["id", "customer", "cc_type", "cc_last_4"]

    @admin.action(
        description="Sync selected payment methods with Authorizenet"
    )
    def sync_with_authorizenet(self, request, queryset):
        for payment in queryset:
            payment.authorizenet_sync()
            payment.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s payment method had its data synced with Authorizenet.",
                "%(count)s payment methods had their data synced with Authorizenet.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]
    list_filter = ["customer"]
    readonly_fields = ["id", "customer", "street"]
    actions = ["sync_with_authorizenet"]

    @admin.action(
        description="Sync selected shipping addresses with Authorizenet"
    )
    def sync_with_authorizenet(self, request, queryset):
        for address in queryset:
            address.authorizenet_sync()
            address.save()

        self.message_user(
            request,
            ngettext(
                "%(count)s shipping address had its data synced with Authorizenet.",
                "%(count)s shipping addresses had their data synced with Authorizenet.",
                len(queryset),
            )
            % {"count": len(queryset)},
            messages.SUCCESS,
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    actions = ["sync_with_authorizenet"]
    list_display = ["id", "customer", "status"]
    list_filter = ["status"]
    readonly_fields = ["status", "payment", "address"]
    view_on_site = False

    @admin.action(description="Sync selected subscriptions with Authorizenet")
    def sync_with_authorizenet(self, request, queryset):
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
    list_display = ["name", "total", "amount", "desc"]
