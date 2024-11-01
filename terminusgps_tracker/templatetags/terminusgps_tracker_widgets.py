from typing import Any, Collection

from django.template import Library

from terminusgps_tracker.models.customer import TodoItem

register = Library()


@register.inclusion_tag(
    "terminusgps_tracker/forms/widgets/address_dropdown.html", takes_context=True
)
def address_dropdown(context: dict[str, Any]) -> dict[str, Any]:
    return {"results": context["results"], "fill_url": context["form_url"]}


@register.inclusion_tag("terminusgps_tracker/forms/widgets/todo_list.html")
def todo_list(todos: Collection[TodoItem]) -> dict[str, Any]:
    return {"todos": todos}
