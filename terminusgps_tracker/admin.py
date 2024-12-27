from django.contrib import admin

from terminusgps_tracker.models import (
    TrackerAsset,
    TrackerAssetCommand,
    TrackerPaymentMethod,
    TrackerProfile,
    TrackerShippingAddress,
    TrackerSubscription,
    TrackerSubscriptionFeature,
    TrackerSubscriptionTier,
)


@admin.register(TrackerPaymentMethod)
class TrackerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile", "is_default"]
    fields = ["authorizenet_id", "profile", "is_default"]
    readonly_fields = ["authorizenet_id"]
    list_display_links = ["profile"]


@admin.register(TrackerShippingAddress)
class TrackerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile", "is_default"]
    fields = ["authorizenet_id", "profile", "is_default"]
    readonly_fields = ["authorizenet_id"]
    list_display_links = ["profile"]


@admin.register(TrackerAsset)
class TrackerAssetAdmin(admin.ModelAdmin):
    list_display = ["name", "profile__user", "is_active"]
    fieldsets = [
        ("Terminus GPS Tracker", {"fields": ["profile", "is_active", "commands"]}),
        ("Wialon", {"fields": ["id", "imei_number", "phone_number", "hw_type"]}),
    ]
    readonly_fields = ["is_active", "hw_type"]


@admin.register(TrackerAssetCommand)
class TrackerAssetCommandAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "link"]
    fields = ["name", "type", "link"]


@admin.register(TrackerProfile)
class TrackerProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Terminus GPS Tracker", {"fields": ["user"]}),
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
    readonly_fields = ["authorizenet_id"]


@admin.register(TrackerSubscription)
class TrackerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user", "status", "tier"]
    list_editable = ["tier"]
    fieldsets = [
        ("Terminus GPS Tracker", {"fields": ["profile", "tier", "status"]}),
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
            "Terminus GPS Tracker",
            {"fields": ["amount", "period", "length", "features"]},
        ),
        ("Wialon", {"fields": ["wialon_id", "wialon_cmd"]}),
    ]
    readonly_fields = ["wialon_id"]
    list_display_links = ["name"]


@admin.register(TrackerSubscriptionFeature)
class TrackerSubscriptionFeatureAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["name", "desc"]})]
    list_display = ["name", "desc"]
