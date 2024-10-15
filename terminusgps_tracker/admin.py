from django.contrib import admin

from terminusgps_tracker.models import CustomerProfile


class CustomerProfileModelAdmin(admin.ModelAdmin):
    list_display = ["user", "aws_sso_id"]
    fieldsets = [
        (None, {"fields": ["user", "aws_sso_id"]}),
        (
            "Authorize.net",
            {
                "fields": [
                    "authorizenet_profile_id",
                    "authorizenet_payment_id",
                    "authorizenet_address_id",
                    "authorizenet_subscription_id",
                ],
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
