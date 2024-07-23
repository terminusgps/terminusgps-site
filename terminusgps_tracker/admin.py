from django.contrib import admin

from .models.customer import Customer, WialonAsset

class WialonAssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "uuid",
        "item_type"
    )

admin.site.register(Customer)
admin.site.register(WialonAsset, WialonAssetAdmin)
