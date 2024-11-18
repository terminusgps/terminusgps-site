from typing import Any

from django.db.models import QuerySet
from django.template import Library

from terminusgps_tracker.integrations.wialon.items.unit import WialonUnit
from terminusgps_tracker.models.todo import TodoItem

register = Library()


@register.inclusion_tag("terminusgps_tracker/profile_todos.html")
def render_todos(todos: QuerySet[TodoItem, TodoItem | None]) -> dict[str, Any]:
    return {"todos": todos}


@register.inclusion_tag("terminusgps_tracker/tooltip.html")
def tooltip(el: str, text: str) -> dict[str, Any]:
    return {"element": el, "text": text}


@register.inclusion_tag("terminusgps_tracker/wialon_asset.html")
def display_wialon_asset(unit_id: str, session_id: str):
    wialon_asset = WialonUnit(id=unit_id, session=session_id)
