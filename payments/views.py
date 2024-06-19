from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from .models import Payment, QuickbooksToken


def auth(request: HttpRequest) -> HttpResponse:
    qb = QuickbooksToken.objects.get_or_create(user=request.user)[0]
    auth_client = qb.create_auth_client()

    if request.GET.get("error", None) is not None:
        context = {
            "title": "Error",
            "error": request.GET["error"],
            "error_description": request.GET["error_description"],
            "state": request.GET["state"],
        }
        return render(request, "payments/oops.html", context=context)

    try:
        auth_code = request.GET["code"]
        realm_id = request.GET["realmId"]

        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        qb.set_access_token(auth_client.access_token)
        qb.set_refresh_token(auth_client.refresh_token)
        qb.save()
    except KeyError:
        return redirect(qb.auth_url(auth_client))

    context = {
        "title": "Quickbooks Authorization",
        "qb": qb,
    }
    return render(request, "payments/auth.html", context=context)


def create_payment(request: HttpRequest) -> HttpResponse | JsonResponse:
    if not request.method == "POST":
        return HttpResponse(status=405)
    else:
        return JsonResponse(
            {
                "status": "success",
            }
        )


def edit_payment(request: HttpRequest, payment_id: int) -> HttpResponse | JsonResponse:
    if not request.method == "POST":
        return HttpResponse(status=405)
    else:
        payment = Payment.objects.get(pk=payment_id)
        return JsonResponse(
            {
                "status": "success",
                "payment": payment,
            }
        )


def cancel_payment(request: HttpRequest, payment_id: int) -> HttpResponse:
    if not request.method == "POST":
        return HttpResponse(status=405)
    else:
        payment = Payment.objects.get(pk=payment_id)
        payment.status = Payment.Status.CANCELED
        context = {
            "title": f"Cancel Payment #{payment_id}",
            "payment": payment,
        }
        return render(request, "payments/payment.html", context=context)


def info(request: HttpRequest, payment_id: int) -> HttpResponse:
    context = {
        "title": "Payment Info",
        "payment": Payment.objects.get(pk=payment_id),
        "user": request.user,
    }
    return render(request, "payments/info.html", context=context)
