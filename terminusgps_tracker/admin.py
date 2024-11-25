from django.contrib import admin

from terminusgps_tracker.models.profile import TrackerProfile
from terminusgps_tracker.models.payment import (
    TrackerPaymentMethod,
    TrackerShippingAddress,
)
from terminusgps_tracker.models import (
    TrackerSubscription,
    TrackerSubscriptionFeature,
    TrackerSubscriptionTier,
)


@admin.register(TrackerProfile)
class TrackerProfileAdmin(admin.ModelAdmin):
    fields = ["user"]
    readonly_fields = ["user"]


@admin.register(TrackerShippingAddress)
class TrackerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user"]
    readonly_fields = ["authorizenet_id", "profile"]


@admin.register(TrackerPaymentMethod)
class TrackerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user", "is_default"]
    fields = ["authorizenet_id", "profile", "is_default"]
    readonly_fields = ["authorizenet_id", "profile", "is_default"]


@admin.register(TrackerSubscription)
class TrackerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile__user", "status", "tier"]
    list_editable = ["tier"]
    fieldsets = [
        (None, {"fields": ["profile", "authorizenet_id"]}),
        ("Details", {"fields": ["tier", "status"]}),
    ]
    readonly_fields = ["authorizenet_id", "profile", "status"]


@admin.register(TrackerSubscriptionTier)
class TrackerSubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "unit_cmd"]
    ordering = ["amount"]
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Data", {"fields": ["group_id", "unit_cmd"]}),
        ("Details", {"fields": ["amount", "period", "length", "features"]}),
    ]
    readonly_fields = ["group_id"]


@admin.register(TrackerSubscriptionFeature)
class TrackerSubscriptionFeatureAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["name", "amount"]})]
