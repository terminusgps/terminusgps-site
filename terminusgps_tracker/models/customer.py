from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from terminusgps_tracker.models.asset import WialonAsset


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(WialonAsset, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.user.username

class CustomerCreationForm(BaseUserCreationForm):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()

    def confirm_login_allowed(self, user: User) -> None:
        if not user.is_active:
            raise ValidationError(_("Sorry, inactivate accounts are not welcome here."))
