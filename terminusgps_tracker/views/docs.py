import markdown
from typing import Any
from pathlib import Path

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe


DOCUMENTATION_PAGES: dict[str, Any] = {
    "privacy": { "path": "privacy_policy.md" },
    "support": { "path": "support.md" },
    "styling": { "path": "styling.md" },
}

def convert_markdown_to_html(document_path: Path) -> str:
    with open(document_path, "r") as doc:
        markdown_content = doc.read()
    html_content = markdown.markdown(markdown_content, extensions=["extra"])
    return mark_safe(html_content)

def documentation_view(request: HttpRequest, page_name: str) -> HttpResponse:
    DOCS_DIR: Path = Path("terminusgps_tracker/docs")
    file_name: str = DOCUMENTATION_PAGES.get(page_name, None)
    if file_name is None:
        return HttpResponse(status=404)
    else:
        DOC_PATH: Path = DOCS_DIR / file_name["path"]
    context = {"document": convert_markdown_to_html(DOC_PATH), "title": page_name.title()}
    return render(request, "terminusgps_tracker/documentation_page.html", context=context)
