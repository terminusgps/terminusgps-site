from typing import Any

from django.template import Library

register = Library()


@register.inclusion_tag(
    "terminusgps_tracker/forms/widgets/address_dropdown.html", takes_context=True
)
def address_dropdown(context: dict[str, Any]) -> dict[str, Any]:
    return {"results": context["results"], "form_url": context["form_url"]}
