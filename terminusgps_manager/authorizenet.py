import logging

from django.conf import settings
from terminusgps.authorizenet.service import AuthorizenetService

logger = logging.getLogger(__name__)


def get_authorizenet_service() -> AuthorizenetService:
    return AuthorizenetService()


def get_hosted_profile_page_url() -> str:
    return (
        "https://accept.authorize.net/customer/manage"
        if not settings.DEBUG
        else "https://test.authorize.net/customer/manage"
    )
