from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from terminusgps_tracker.models.service import AuthService, AuthToken


def auth_view(request: HttpRequest, service_name: str) -> HttpResponse:
    if service_name.upper() not in AuthService.AuthServiceName.__members__:
        return HttpResponse(status=404)
    
    service = AuthService.objects.filter(name__contains=service_name.upper()).first()
    token, created = AuthToken.objects.get_or_create(
        user=request.user,
        service=service,
    )

    if created or token.expiry_date is None:
        return redirect(service.auth_url)
    elif token.expiry_date < timezone.now():
        token.refresh(service.auth_url)
