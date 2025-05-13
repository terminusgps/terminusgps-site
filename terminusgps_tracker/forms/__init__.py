from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if settings.configured and not hasattr(settings, "DEFAULT_FIELD_CLASS"):
    raise ImproperlyConfigured("'DEFAULT_FIELD_CLASS' setting is required.")

from .addresses import CustomerShippingAddressCreateForm
from .assets import CustomerAssetCreateForm
from .payments import CustomerPaymentMethodCreateForm
from .subscriptions import CustomerSubscriptionUpdateForm
