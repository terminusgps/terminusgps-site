from typing import Any

from django.db.models import QuerySet
from django.template import Library

from terminusgps_tracker.models.customer import TodoItem

register = Library()


@register.inclusion_tag("terminusgps_tracker/profile_todos.html")
def render_todos(todos: QuerySet[TodoItem, TodoItem | None]) -> dict[str, Any]:
    return {"todos": todos}
