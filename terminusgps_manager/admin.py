from django.contrib import admin

from . import models


@admin.register(models.TerminusProfile)
class TerminusProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.ContactFormResponse)
class ContactFormResponseAdmin(admin.ModelAdmin):
    date_hierarchy = "submit_date"
    list_display = ["email", "full_name", "submit_date"]
    readonly_fields = [
        "full_name",
        "email",
        "phone",
        "city",
        "state",
        "message",
    ]
