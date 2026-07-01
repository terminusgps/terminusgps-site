from django.contrib import admin, messages
from django.utils.translation import ngettext

from . import models


@admin.register(models.ContactFormResponse)
class ContactFormResponseAdmin(admin.ModelAdmin):
    actions = ["email_admins"]
    list_display = ["name", "pub_date"]
    date_hierarchy = "pub_date"

    @admin.action(description="Email selected responses to admins")
    def email_admins(self, request, queryset):
        for response in queryset:
            response.email_to_admins()
        self.message_user(
            request,
            ngettext(
                "%d response was successfully emailed.",
                "%d responses were successfully emailed.",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )
