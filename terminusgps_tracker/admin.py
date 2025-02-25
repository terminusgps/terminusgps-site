from django.contrib import admin
from django.db import models
from django.forms import widgets
from django.utils.translation import ngettext
from django.contrib import messages

from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.models import (
    TrackerAsset,
    TrackerPaymentMethod,
    TrackerProfile,
    TrackerShippingAddress,
    TrackerSubscription,
    TrackerSubscriptionFeature,
    TrackerSubscriptionTier,
)


@admin.register(TrackerPaymentMethod)
class TrackerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile", "default"]
    fields = ["authorizenet_id", "profile", "default"]
    readonly_fields = ["authorizenet_id"]
    list_display_links = ["profile"]


@admin.register(TrackerShippingAddress)
class TrackerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["authorizenet_id", "profile", "default"]
    fields = ["authorizenet_id", "profile", "default"]
    readonly_fields = ["authorizenet_id"]
    list_display_links = ["profile"]


@admin.register(TrackerAsset)
class TrackerAssetAdmin(admin.ModelAdmin):
    list_display = ["name", "profile__user", "is_active"]
    fieldsets = [
        ("Terminus GPS Tracker", {"fields": ["profile", "is_active"]}),
        ("Wialon", {"fields": ["wialon_id", "imei_number", "phone_number", "hw_type"]}),
    ]
    readonly_fields = ["is_active", "hw_type", "imei_number", "phone_number"]
    actions = ["repopulate_asset"]

    @admin.action(description="Repopulate selected assets using the Wialon API")
    def repopulate_asset(self, request, queryset):
        num_assets = len(queryset)
        with WialonSession() as session:
            for asset in queryset:
                asset.save(session=session)
        self.message_user(
            request,
            ngettext(
                "%(count)s asset was successfully repopulated.",
                "%(count)s assets were successfully repopulated.",
                num_assets,
            )
            % {"count": num_assets},
            messages.SUCCESS,
        )


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
    readonly_fields = ["wialon_id", "period", "length"]
    list_display_links = ["name"]


@admin.register(TrackerSubscriptionFeature)
class TrackerSubscriptionFeatureAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["name", "desc"]})]
    list_display = ["name", "desc"]
    formfield_overrides = {
        models.TextField: {"widget": widgets.Textarea(attrs={"rows": 4, "cols": 40})}
    }
