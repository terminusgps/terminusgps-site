from django.contrib import admin

from .models.asset import WialonAsset
from .models.customer import Customer
from .models.service import AuthService, AuthServiceImage


class WialonAssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "uuid",
        "item_type"
    )

class AuthServiceAdmin(admin.ModelAdmin):
    exclude = ["_access_token", "_refresh_token", "_auth_code"]
    list_display = (
        "user",
        "state"
    )

class AuthServiceImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "service_type",
        "image_type",
    )

admin.site.register(Customer)
admin.site.register(WialonAsset, WialonAssetAdmin)
admin.site.register(AuthService, AuthServiceAdmin)
admin.site.register(AuthServiceImage, AuthServiceImageAdmin)
