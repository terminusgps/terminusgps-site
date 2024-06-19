from django.contrib import admin

from .models import Payment, QuickbooksToken

admin.site.register(Payment)
admin.site.register(QuickbooksToken)
