from typing import Any

from django.template import Library

register = Library()


@register.inclusion_tag(
    "terminusgps_tracker/forms/address_dropdown.html", takes_context=True
)
def address_dropdown(context: dict[str, Any]) -> dict[str, Any]:
    return {"results": context["results"], "fill_url": context["form_url"]}


@register.inclusion_tag(
    "terminusgps_tracker/forms/widgets/todo_list.html", takes_context=True
)
def display_todo_list(context: dict[str, Any]) -> dict[str, Any]:
    return {"todos": context["profile"].todo_list.items.all()}
