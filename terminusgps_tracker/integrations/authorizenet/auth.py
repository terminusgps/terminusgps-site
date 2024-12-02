from authorizenet.apicontractsv1 import merchantAuthenticationType

from django.conf import settings


def get_merchant_auth() -> merchantAuthenticationType:
    return merchantAuthenticationType(
        name=str(settings.MERCHANT_AUTH_LOGIN_ID),
        transactionKey=str(settings.MERCHANT_AUTH_TRANSACTION_KEY),
    )
