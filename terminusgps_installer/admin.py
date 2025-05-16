from django.contrib import admin

from .models import Installer, WialonAccount


@admin.register(Installer)
class InstallerAdmin(admin.ModelAdmin):
    list_display = ["user"]


@admin.register(WialonAccount)
class WialonAccountAdmin(admin.ModelAdmin):
    list_display = ["name"]
