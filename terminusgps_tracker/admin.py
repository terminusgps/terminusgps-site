from django.contrib import admin

from terminusgps_tracker.models.profile import TrackerProfile
from terminusgps_tracker.models.payment import (
    TrackerPaymentMethod,
    TrackerShippingAddress,
)
from terminusgps_tracker.models.subscription import (
    TrackerSubscription,
    TrackerSubscriptionFeature,
    TrackerSubscriptionTier,
)
from terminusgps_tracker.models.todo import TrackerTodoList, TodoItem


@admin.register(TrackerShippingAddress)
class TrackerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["profile", "authorizenet_id", "is_default"]
    readonly_fields = ["profile", "authorizenet_id"]


@admin.register(TrackerProfile)
class TrackerProfileAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "authorizenet_profile_id",
        "wialon_super_user_id",
        "wialon_user_id",
        "wialon_group_id",
        "wialon_resource_id",
    ]
    readonly_fields = [
        "user",
        "authorizenet_profile_id",
        "wialon_super_user_id",
        "wialon_user_id",
        "wialon_group_id",
        "wialon_resource_id",
    ]


@admin.register(TrackerTodoList)
class TrackerTodoListAdmin(admin.ModelAdmin):
    fields = ["profile"]


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ["todo_list__profile__user", "label", "view", "is_complete"]
    fields = ["todo_list__profile__user", "label", "view", "is_complete"]


@admin.register(TrackerPaymentMethod)
class TrackerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["id", "profile__user__username", "is_default"]
    fields = ["profile", "is_default"]
    readonly_fields = ["id", "profile"]


@admin.register(TrackerSubscription)
class TrackerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["profile__user__username", "curr_tier"]
    list_editable = ["curr_tier"]


@admin.register(TrackerSubscriptionTier)
class TrackerSubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "amount", "unit_cmd"]
    ordering = ["amount"]
    fieldsets = [
        (None, {"fields": ["name"]}),
        ("Wialon", {"fields": ["wialon_group_id", "unit_cmd"]}),
        ("Details", {"fields": ["amount", "period", "length", "features"]}),
    ]
    readonly_fields = ["wialon_group_id"]


@admin.register(TrackerSubscriptionFeature)
class TrackerSubscriptionFeatureAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["name", "amount"]})]
