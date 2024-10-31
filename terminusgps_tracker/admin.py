from django.contrib import admin

from terminusgps_tracker.models import CustomerProfile


class CustomerProfileModelAdmin(admin.ModelAdmin):
    list_display = ["user", "wialon_user_id"]
    fieldsets = [
        (None, {"fields": ["user"]}),
        (
            "Authorize.net",
            {
                "fields": ["authorizenet_profile_id", "payments", "addresses"],
                "classes": ["collapse"],
            },
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


admin.site.register(CustomerProfile, CustomerProfileModelAdmin)
