from django.contrib import admin

from terminusgps_tracker.models import (
    TrackerProfile,
    TrackerPaymentMethod,
    TrackerShippingAddress,
    TrackerSubscription,
    TrackerSubscriptionFeature,
    TrackerSubscriptionTier,
)


@admin.register(TrackerPaymentMethod)
class TrackerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user", "is_default"]
    fields = ["authorizenet_id", "profile", "is_default"]
    readonly_fields = ["authorizenet_id", "profile", "is_default"]


@admin.register(TrackerProfile)
class TrackerProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Tracker", {"fields": ["user"]}),
        ("Authorize.NET", {"fields": ["authorizenet_id"]}),
        (
            "Wialon",
            {
                "fields": [
                    "wialon_super_user_id",
                    "wialon_end_user_id",
                    "wialon_group_id",
                    "wialon_resource_id",
                ]
            },
        ),
    ]
    readonly_fields = [
        "authorizenet_id",
        "wialon_super_user_id",
        "wialon_end_user_id",
        "wialon_group_id",
        "wialon_resource_id",
    ]


@admin.register(TrackerShippingAddress)
class TrackerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user"]
    readonly_fields = ["authorizenet_id", "profile"]


@admin.register(TrackerSubscription)
class TrackerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user", "status", "tier"]
    list_editable = ["tier"]
    fieldsets = [
        ("Tracker", {"fields": ["profile", "tier", "status"]}),
        ("Authorize.NET", {"fields": ["authorizenet_id"]}),
    ]
    readonly_fields = ["authorizenet_id", "profile", "status"]


@admin.register(TrackerSubscriptionTier)
class TrackerSubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["wialon_id", "name", "amount"]
    ordering = ["amount"]
    fieldsets = [
        (None, {"fields": ["name"]}),
        (
            "Wialon",
            {
                "fields": [
                    "wialon_id",
                    "wialon_cmd",
                    "wialon_cmd_link",
                    "wialon_cmd_type",
                ]
            },
        ),
        ("Tracker", {"fields": ["amount", "period", "length", "features"]}),
    ]
    readonly_fields = ["wialon_id"]


@admin.register(TrackerSubscriptionFeature)
class TrackerSubscriptionFeatureAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["name", "amount"]})]
