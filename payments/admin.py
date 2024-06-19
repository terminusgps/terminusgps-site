from django.contrib import admin

from .models import LightmetricsToken, QuickbooksToken

admin.site.register(LightmetricsToken)
admin.site.register(QuickbooksToken)
