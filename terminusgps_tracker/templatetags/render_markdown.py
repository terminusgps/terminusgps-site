import logging
import markdown
from bleach import clean
from bs4 import BeautifulSoup
from pathlib import Path

from django import template
from django.template.loader import render_to_string
from django.template.defaultfilters import stringfilter

register = template.Library()
logger = logging.getLogger(__name__)

ALLOWED_TAGS: list[str] = [
    "a",
    "blockquote",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "ul",
]
ALLOWED_ATTRS: dict[str, list[str]] = {
    "a": ["href"]
}

def sanitize_html_content(
    html_content: str,
    allowed_tags: list[str] = ALLOWED_TAGS,
    allowed_attrs: dict[str, list[str]] = ALLOWED_ATTRS
) -> str:
    """Sanitizes input html content and returns it."""
    return clean(html_content, tags=allowed_tags, attributes=allowed_attrs)

@register.filter(needs_autoescape=True)
@stringfilter
def render_markdown(value: str, autoescape: bool = True) -> str:
    """Takes a markdown document filename and returns styled and sanitized html content."""
    DOCS_DIR: Path = Path("terminusgps_tracker/docs")
    DOC_PATH: Path = DOCS_DIR / value

    if not DOC_PATH.exists():
        raise FileNotFoundError(f"File '{DOC_PATH}' does not exist.")
    else:
        with open(DOC_PATH, "r") as doc:
            md_content = doc.read()
            html_content = sanitize_html_content(markdown.markdown(md_content))
            soup = BeautifulSoup(html_content, "html.parser")

            context = {"elements": soup.find_all()}
            print(context)
            return render_to_string("terminusgps_tracker/_doc_styles.html", request=None, context=context)
