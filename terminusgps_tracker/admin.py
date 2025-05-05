from django.contrib import admin, messages
from django.utils.translation import ngettext
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models.customers import (
    Customer,
    CustomerAsset,
    CustomerPaymentMethod,
    CustomerShippingAddress,
)
from terminusgps_tracker.models.subscriptions import (
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
        "block_customer_accounts",
        "unblock_customer_accounts",
    ]
    fieldsets = [
        (None, {"fields": ["user", "email_verified"]}),
        ("Authorizenet", {"fields": ["authorizenet_id"]}),
        ("Wialon", {"fields": ["wialon_user_id", "wialon_resource_id"]}),
    ]
    readonly_fields = ["email_verified"]

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

    @admin.action(description="Block selected customer accounts")
    def block_customer_accounts(self, request, queryset):
        results_map = {"success": [], "skipped": []}
        with WialonSession() as session:
            for customer in queryset:
                if not customer.wialon_resource_id:
                    results_map["skipped"].append(customer)
                    continue
                customer.wialon_disable_account(session)
                results_map["success"].append(customer)

        if results_map["skipped"]:
            self.message_user(
                request,
                ngettext(
                    "%(count)s customer account was skipped.",
                    "%(count)s customer accounts were skipped.",
                    len(results_map["skipped"]),
                )
                % {"count": len(results_map["skipped"])},
                messages.WARNING,
            )

        if results_map["success"]:
            self.message_user(
                request,
                ngettext(
                    "%(count)s customer account was disabled.",
                    "%(count)s customer accounts were disabled.",
                    len(results_map["success"]),
                )
                % {"count": len(results_map["success"])},
                messages.SUCCESS,
            )

    @admin.action(description="Unblock selected customer accounts")
    def unblock_customer_accounts(self, request, queryset):
        results_map = {"success": [], "skipped": []}

        with WialonSession() as session:
            for customer in queryset:
                if not customer.wialon_resource_id:
                    results_map["skipped"].append(customer)
                    continue
                customer.wialon_enable_account(session)
                results_map["success"].append(customer)

        if results_map["skipped"]:
            self.message_user(
                request,
                ngettext(
                    "%(count)s customer account was skipped.",
                    "%(count)s customer accounts were skipped.",
                    len(results_map["skipped"]),
                )
                % {"count": len(results_map["skipped"])},
                messages.WARNING,
            )

        if results_map["success"]:
            self.message_user(
                request,
                ngettext(
                    "%(count)s customer account was enabled.",
                    "%(count)s customer accounts were enabled.",
                    len(results_map["success"]),
                )
                % {"count": len(results_map["success"])},
                messages.SUCCESS,
            )


@admin.register(CustomerAsset)
class CustomerAssetAdmin(admin.ModelAdmin):
    list_display = ["customer"]
    list_filter = ["customer"]


@admin.register(CustomerPaymentMethod)
class CustomerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer"]
    list_filter = ["customer"]
    view_on_site = False


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer"]
    list_filter = ["customer"]
    view_on_site = False


@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "customer", "status"]
    list_filter = ["status"]
    readonly_fields = ["status"]
    actions = ["refresh_subscriptions_status"]

    @admin.action(description="Refresh selected subscription statuses")
    def refresh_subscriptions_status(self, request, queryset):
        [sub.authorizenet_refresh_status() for sub in queryset if sub.authorizenet_id]
        self.message_user(
            request,
            ngettext(
                "Refreshed %(count)s subscription status.",
                "Refreshed %(count)s subscription statuses.",
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
