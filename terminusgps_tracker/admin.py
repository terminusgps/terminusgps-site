from django.contrib import admin

from .models.asset import WialonAsset
from .models.customer import Customer


class WialonAssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "uuid",
        "item_type"
    )

admin.site.register(Customer)
admin.site.register(WialonAsset, WialonAssetAdmin)
