import markdown
from pathlib import Path
from typing import Union

from django.utils.safestring import mark_safe
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


DOCS_DIR = Path("terminusgps_tracker/docs")
PAGES: dict[str, dict[str, Union[str, Path]]] = {
    "support": {
        "title": "Support",
        "subtitle": "Support Documentation Subtitle",
        "filepath": DOCS_DIR / "support.md",
    },
    "about": {
        "title": "About",
        "subtitle": "About Documentation Subtitle",
        "filepath": DOCS_DIR / "about.md",
    },
    "branding": {
        "title": "Branding",
        "subtitle": "Branding Documentation Subtitle",
        "filepath": DOCS_DIR / "branding.md",
    },
}

def convert_markdown_to_html(document_path: Path) -> str:
    with open(document_path, "r") as doc:
        markdown_content = doc.read()
    html_content = markdown.markdown(markdown_content, extensions=["extra"])
    return mark_safe(html_content)

def documentation_index(request: HttpRequest) -> HttpResponse:
    context = {"pages": PAGES}
    return render(request, "terminusgps_tracker/documentation_index.html", context=context)

def documentation_view(request: HttpRequest, page_name: str) -> HttpResponse:
    document = PAGES.get(page_name, None)
    if document is None:
        return HttpResponse(status=404)
    context = {
        "title": document["title"],
        "subtitle": document["subtitle"],
        "markdown": convert_markdown_to_html(document["filepath"])
    }
    return render(request, "terminusgps_tracker/documentation_page.html", context=context)
