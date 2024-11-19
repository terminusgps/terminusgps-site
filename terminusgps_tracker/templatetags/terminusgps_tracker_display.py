from typing import Any

from django.template import Library
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

    return {
        "label": todo.label,
        "url": todo.get_absolute_url(),
        "complete": todo.is_complete,
        "svg": svg_str,
    }


@register.inclusion_tag("terminusgps_tracker/subscription_card.html")
def render_subscription_card(tier: TrackerSubscriptionTier) -> dict[str, Any]:
    return {"name": tier.name, "rate": tier.amount}
