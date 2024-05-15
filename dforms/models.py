from django.db.models import functions
from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=36)
    logo = models.ImageField()

    def __str__(self) -> str:
        return self.name


class RegistrationFormSubmission(models.Model):
    first_name = models.CharField(max_length=24)
    last_name = models.CharField(max_length=24)
    email = models.EmailField(max_length=64)
    asset_name = models.CharField(max_length=256)
    imei = models.IntegerField()
    phone = models.CharField(max_length=24)
    date_submitted = models.DateTimeField(
        blank=True, null=False, db_default=functions.Now()
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} registered {self.asset_name}"


class NewsletterSignupSubmission(models.Model):
    email = models.EmailField(max_length=64)
    opted_in = models.BooleanField(default=False)
    date_submitted = models.DateTimeField(
        blank=True, null=False, db_default=functions.Now()
    )

    def __str__(self) -> str:
        return self.email
