from django import template
from django.utils.safestring import SafeString, mark_safe

register = template.Library()


@register.filter(name="human_readable")
def human_readable(text: str) -> SafeString:
    if "_" in text:
        text_parts = text.split("_")
        text = " ".join(text_parts)
    return mark_safe(text)
