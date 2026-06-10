from django.contrib.auth.decorators import login_required
from django.http import HttpRequest as HttpRequestBase
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.views.decorators.vary import vary_on_headers

from .decorators import htmx_template
from .models import TerminusProfile


class HttpRequest(HttpRequestBase):
    template_name: str


@vary_on_headers("HX-Request")
@cache_control(private=True, max_age=300)
@htmx_template("manager/dashboard.html")
@require_GET
@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    profile, created = TerminusProfile.objects.get_or_create(user=request.user)
    context = {"profile": profile, "created": created}
    return TemplateResponse(request, request.template_name, context)
