from bleach import clean

from .markdown_config import ALLOWED_ATTRS, ALLOWED_TAGS

def sanitize_html_content(html_content: str) -> str:
    """Sanitizes HTML content based on the ALLOWED_ATTRS and ALLOWED_TAGS configuration."""
    return clean(html_content, attributes=ALLOWED_ATTRS, tags=ALLOWED_TAGS)
