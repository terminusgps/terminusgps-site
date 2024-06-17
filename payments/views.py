from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Payment


def quickbooks_consent(request: HttpRequest) -> HttpResponse:
    context = {"title": "Quickbooks Consent", "auth_url": "https://google.com/"}
    return render(request, "payments/consent.html", context=context)


def quickbooks_auth(request: HttpRequest) -> HttpResponse | JsonResponse:
    if not request.method == "GET":
        return HttpResponse(status=405)
    else:
        code = request.GET.get("code", "")
        state = request.GET.get("state", "")
        realmId = request.GET.get("realmId", "")

        return JsonResponse(
            {
                "code": code,
                "state": state,
                "realmId": realmId,
            }
        )


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
