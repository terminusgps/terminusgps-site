import logging

from authorizenet import apicontractsv1
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps_payments.services import AuthorizenetService

logger = logging.getLogger(__name__)
service = AuthorizenetService()


def update_customer_subscription_amount(sender, **kwargs):
    try:
        if customer_unit := kwargs.get("instance"):
            if subscription := customer_unit.customer.subscription:
                new_amount = (
                    customer_unit.customer.get_subscription_grand_total()
                )
                anet_subscription = apicontractsv1.ARBSubscriptionType()
                anet_subscription.amount = new_amount
                service.update_subscription(subscription, anet_subscription)
                subscription.amount = new_amount
                subscription.save(update_fields=["amount"])
    except (AuthorizenetControllerExecutionError, ValueError) as e:
        logger.error(str(e))
        raise
