import markdown
from pathlib import Path
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from terminusgps_tracker.utils.sanitization import sanitize_html_content
from terminusgps_tracker.utils.markdown_processors import DataAttributeExtension


def documentation_view(request: HttpRequest, page_name: str) -> HttpResponse:
    DOC_DIR: Path = Path("terminusgps_tracker/docs")
    DOC_PATH: Path = DOC_DIR / f"{page_name}.md"
    if not DOC_PATH.exists():
        return HttpResponse(status=404)

    with open(DOC_PATH, "r") as doc:
        markdown_content = sanitize_html_content(doc.read())
        html_content = markdown.markdown(markdown_content, extensions=[DataAttributeExtension()])

    context: dict[str, Any] = {
        "title": page_name.title(),
        "content": html_content,
    }
    print(sanitize_html_content(html_content))
    return render(request, "terminusgps_tracker/documentation_page.html", context=context)
