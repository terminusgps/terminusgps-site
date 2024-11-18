from django.contrib import admin

from terminusgps_tracker.models.profile import TrackerProfile
from terminusgps_tracker.models.payment import TrackerPaymentMethod
from terminusgps_tracker.models.subscription import TrackerSubscription
from terminusgps_tracker.models.todo import TrackerTodoList, TodoItem


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


@admin.register(TrackerPaymentMethod)
class TrackerPaymentMethodAdmin(admin.ModelAdmin):
    fields = ["id", "profile"]


@admin.register(TrackerSubscription)
class TrackerSubscriptionAdmin(admin.ModelAdmin):
    fields = ["id", "profile"]


@admin.register(TrackerTodoList)
class TrackerTodoListAdmin(admin.ModelAdmin):
    fields = ["items", "profile"]


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    fields = ["label", "view", "is_complete"]
