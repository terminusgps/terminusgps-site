from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from terminusgps_tracker.models.token import AuthToken


def auth_view(request: HttpRequest, service_type: str) -> HttpResponse:
    if service_type.upper() not in AuthToken.ServiceType.__members__:
        return HttpResponse(status=404)

    token, _ = AuthToken.objects.get_or_create(
        user=request.user,
        service_type=service_type.upper(),
    )
    context = {
        "title": f"Authorize {service_type.title()}",
        "token": token,
        "client": token.get_client(settings.CLIENT_ID),
    }
    return render(request, "terminusgps_tracker/auth.html", context=context)
