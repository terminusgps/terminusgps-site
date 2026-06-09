import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET

from .decorators import persistent_wialon_session
from .models import TerminusProfile

logger = logging.getLogger(__name__)


def request_is_htmx(request: HttpRequest) -> bool:
    hx_request = bool(request.headers.get("HX-Request"))
    hx_boosted = bool(request.headers.get("HX-Boosted"))
    return hx_request and not hx_boosted


@require_GET
@login_required
@persistent_wialon_session
def dashboard_view(request: HttpRequest) -> HttpResponse:
    template_name = "manager/dashboard.html"
    if request_is_htmx(request):
        template_name = template_name + "#main"
    profile, created = TerminusProfile.objects.get_or_create(user=request.user)
    context = {"profile": profile, "created": created}
    return TemplateResponse(request, template_name, context)
