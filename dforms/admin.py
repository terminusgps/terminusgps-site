from django.contrib import admin

from .models import (
    Client,
    RegistrationFormSubmission,
    NewsletterSignupSubmission,
)

admin.site.register(Client)
admin.site.register(RegistrationFormSubmission)
admin.site.register(NewsletterSignupSubmission)
