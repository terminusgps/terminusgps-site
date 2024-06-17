import os

from cryptography.fernet import Fernet
from django.db import models
from django.utils.translation import gettext_lazy as _

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "")


class QuickbooksAuth(models.Model):
    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    refresh_token = models.TextField()
    access_token = models.TextField()
    token_expiry = models.DateTimeField()

    def encrypt_token(self, token: str):
        f = Fernet(ENCRYPTION_KEY)
        return f.encrypt(token.encode()).decode()

    def decrypt_token(self, token: str):
        f = Fernet(ENCRYPTION_KEY)
        return f.decrypt(token.encode()).decode()

    def set_refresh_token(self, refresh_token: str):
        self.refresh_token = self.encrypt_token(refresh_token)

    def get_refresh_token(self):
        return self.decrypt_token(self.refresh_token)

    def set_access_token(self, access_token):
        self.access_token = self.encrypt_token(access_token)

    def get_access_token(self):
        return self.decrypt_token(self.access_token)


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "CR", _("Order was created.")
        APPROVED = "AP", _("Order was approved by admin.")
        PAID = "PA", _("Order was paid by user.")
        CANCELED = "CA", _("Order was canceled.")

    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.CREATED,
    )

    def __str__(self):
        return f"{self.user.username} - ${self.amount}"
