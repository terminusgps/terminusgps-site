from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .models.tokens import LightmetricsToken


def authorize(request: HttpRequest, service: str) -> HttpResponse:
    user = request.user
    match service:
        case "lightmetrics" | "lm":
            token, created = LightmetricsToken.objects.get_or_create(user=user)
        case "quickbooks" | "qb":
            token, created = QuickbooksToken.objects.get_or_create(user=user)
        case "square" | "squareup" | "sq":
            token, created = SquareupToken.objects.get_or_create(user=user)
        case "stripe" | "st":
            token, created = StripeToken.objects.get_or_create(user=user)
        case _:
            raise ValueError("Unknown service.")

    context = {
        "title": f"Authorize {service}",
        "token": token,
        "token_created": created,
    }
    return render(request, "payments/authorize.html", context=context)
