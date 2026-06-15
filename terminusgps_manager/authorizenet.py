import logging

from django.conf import settings
from lxml.objectify import ObjectifiedElement
from terminusgps.authorizenet import api
from terminusgps.authorizenet.service import (
    AuthorizenetError,
    AuthorizenetService,
)

logger = logging.getLogger(__name__)


def get_authorizenet_service() -> AuthorizenetService:
    return AuthorizenetService()


def get_hosted_profile_page_url() -> str:
    return (
        "https://accept.authorize.net/customer/manage"
        if not settings.DEBUG
        else "https://test.authorize.net/customer/manage"
    )


def get_customer_profile_by_email(email: str) -> ObjectifiedElement | None:
    anet_service = get_authorizenet_service()
    anet_request = api.get_customer_profile(email=email)
    try:
        anet_response = anet_service.execute(anet_request)
    except AuthorizenetError as error:
        logger.error(error)
        return
    else:
        return anet_response.profile
