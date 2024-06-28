from django.contrib import admin

from .models import QuickbooksToken
from .models.forms import AssetForm, ContactForm, PersonForm, RegistrationForm


class AssetFormAdmin(admin.ModelAdmin):
    list_display = [
        "asset_name",
        "imei_number",
    ]


class ContactFormAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "phone_number",
    ]


class PersonFormAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
    ]


admin.site.register(AssetForm)
admin.site.register(ContactForm)
admin.site.register(PersonForm)
admin.site.register(QuickbooksToken)
admin.site.register(RegistrationForm)
