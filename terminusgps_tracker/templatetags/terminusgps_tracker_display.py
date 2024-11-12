from typing import Any

from django.db.models import QuerySet
from django.template import Library

from terminusgps_tracker.models.customer import TodoItem
from terminusgps_tracker.models.subscription import TrackerSubscription

register = Library()


@register.inclusion_tag("terminusgps_tracker/display_todos.html")
def display_todos(todos: QuerySet[TodoItem, TodoItem | None]) -> dict[str, Any]:
    return {"todos": todos}


@register.inclusion_tag("terminusgps_tracker/display_subscription.html")
def display_subscription(subscription: TrackerSubscription) -> dict[str, Any]:
    data_dict = {}

    data_dict["name"] = subscription.get_tier_display()
    data_dict["rate"] = subscription.get_rate(tier=subscription.tier)
    data_dict["amount"] = subscription.amount
    match subscription.tier:
        case TrackerSubscription.SubscriptionTier.COPPER:
            data_dict["tier"] = "Cu"
        case TrackerSubscription.SubscriptionTier.SILVER:
            data_dict["tier"] = "Ag"
        case TrackerSubscription.SubscriptionTier.GOLD:
            data_dict["tier"] = "Au"
        case _:
            data_dict["tier"] = None
    return data_dict
