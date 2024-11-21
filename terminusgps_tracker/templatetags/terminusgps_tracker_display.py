from typing import Any

from django.template import Library
from django.urls import reverse_lazy
from django.utils.safestring import SafeString, mark_safe

from terminusgps_tracker.models.subscription import TrackerSubscriptionTier
from terminusgps_tracker.models.todo import TodoItem

register = Library()


@register.inclusion_tag("terminusgps_tracker/todo_item.html")
def render_todo_item(todo: TodoItem) -> dict[str, Any]:
    if todo.is_complete:
        svg_str: SafeString = mark_safe(
            '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 text-green-500"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>'
        )
    else:
        svg_str: SafeString = mark_safe(
            '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6 text-red-500"><path stroke-linecap="round" stroke-linejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>'
        )

    return {"label": todo.label, "url": todo.get_absolute_url(), "svg": svg_str}


@register.inclusion_tag("terminusgps_tracker/subscription_card.html")
def render_subscription_card(tier: TrackerSubscriptionTier) -> dict[str, Any]:
    match tier.name:
        case "Copper":
            bg_gradient: str = "from-orange-700 via-orange-300 to-orange-700"
            text_color: str = "#f4f4f4"
        case "Silver":
            bg_gradient: str = "from-gray-700 via-gray-300 to-gray-700"
            text_color: str = "#f4f4f4"
        case "Gold":
            bg_gradient: str = "from-yellow-700 via-yellow-300 to-yellow-700"
            text_color: str = "#f4f4f4"
        case "Platinum":
            bg_gradient: str = "from-gray-500 via-gray-100 to-gray-500"
            text_color: str = "#f4f4f4"
        case _:
            bg_gradient: str = "from-gray-700 via-gray-300 to-gray-700"
            text_color: str = "#f4f4f4"
    print({feature.name: feature.amount for feature in tier.features.all()})
    return {
        "name": tier.name,
        "amount": tier.amount,
        "features": {feature.name: feature.amount for feature in tier.features.all()},
        "text_color": text_color,
        "bg_gradient": bg_gradient,
        "select_url": reverse_lazy("profile create subscription"),
    }


@register.inclusion_tag("terminusgps_tracker/payment_method.html")
def render_payment_profile(payment_profile) -> dict[str, Any]:
    return {
        "card": {
            "number": payment_profile.payment.creditCardNumber,
            "type": payment_profile.payment.creditCardType,
        },
        "address": {
            "full_name": f"{payment_profile.billTo.firstName} {payment_profile.billTo.lastName}",
            "street": payment_profile.billTo.address,
            "city": payment_profile.billTo.city,
            "state": payment_profile.billTo.state,
            "zip": payment_profile.billTo.zip,
            "country": payment_profile.billTo.country,
            "phone": payment_profile.billTo.phoneNumber,
        },
    }
