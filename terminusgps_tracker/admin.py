from django.contrib import admin

from terminusgps_tracker.models.customer import TrackerProfile, TodoItem, TodoList
from terminusgps_tracker.models.subscription import TrackerSubscription


@admin.register(TrackerSubscription)
class TrackerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["name", "rate", "tier"]
    fieldsets = [
        (None, {"fields": ["name", "tier", "duration"]}),
        ("readonly", {"fields": ["rate", "gradient"]}),
    ]


@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ["label", "view", "is_complete"]


@admin.register(TodoList)
class TodoListAdmin(admin.ModelAdmin):
    fieldsets = [(None, {"fields": ["items"]})]


@admin.register(TrackerProfile)
class TrackerProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "subscription", "wialon_user_id"]
    fieldsets = [
        (None, {"fields": ["user"]}),
        (
            "Authorize.net",
            {"fields": ["authorizenet_profile_id"], "classes": ["collapse"]},
        ),
        (
            "Wialon",
            {
                "fields": [
                    "wialon_super_user_id",
                    "wialon_user_id",
                    "wialon_group_id",
                    "wialon_resource_id",
                ],
                "classes": ["collapse"],
            },
        ),
    ]
