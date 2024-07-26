from django.contrib import admin

from .models.asset import WialonAsset
from .models.customer import Customer
from .models.service import AuthService, AuthServiceImage

admin.site.register(Customer)
admin.site.register(WialonAsset)
admin.site.register(AuthService)
admin.site.register(AuthServiceImage)
