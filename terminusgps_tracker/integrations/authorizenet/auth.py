from authorizenet.apicontractsv1 import merchantAuthenticationType

from django.conf import settings


def get_merchant_auth() -> merchantAuthenticationType:
    return settings.MERCHANT_AUTHENTICATION
