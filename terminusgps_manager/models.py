from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class TerminusProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="terminus_profile",
    )
    wialon_user_id = models.CharField(blank=True)
    wialon_resource_id = models.CharField(blank=True)
    authorizenet_customer_profile_id = models.CharField(blank=True)
    authorizenet_subscription_id = models.CharField(blank=True)

    class Meta:
        verbose_name = _("terminus profile")
        verbose_name_plural = _("terminus profiles")

    def __str__(self) -> str:
        return str(self.user)


class ContactFormResponse(models.Model):
    full_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=255)
    phone = PhoneNumberField(blank=True)
    city = models.CharField(blank=True)
    state = models.CharField(blank=True)
    message = models.TextField(max_length=2048)
    submit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("contact form response")
        verbose_name_plural = _("contact form responses")

    def __str__(self) -> str:
        return str(self.email)
