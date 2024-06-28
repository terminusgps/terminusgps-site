from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from terminusgps_tracker.models.wialon import WialonToken

from .decorators import requires_wialon_token
from .models.forms import AssetForm, ContactForm, PersonForm, RegistrationForm
from .wialonapi import WialonQuery, WialonSession


def dashboard(request: HttpRequest) -> HttpResponse:
    wialon_token, created = WialonToken.objects.get_or_create(user=request.user)
    if created:
        return auth(request, "wialon")
    context = {
        "title": "Dashboard",
    }
    return render(request, "terminusgps_tracker/dashboard.html", context=context)


def auth(request: HttpRequest, service: str) -> HttpResponse:
    match service:
        case "wialon":
            token = WialonToken.objects.get_or_create(user=request.user)[0]
            context = {
                "title": "Wialon Authentication",
                "auth_url": token.auth_url,
            }
        case "lightmetrics":
            raise NotImplementedError
        case _:
            return HttpResponse(status=400)
    return render(request, "terminusgps_tracker/auth.html", context=context)


def oauth2_callback(request: HttpRequest, service: str) -> HttpResponse:
    user = request.user
    match service:
        case "wialon":
            token = WialonToken.objects.get(user=user)
            token.access_token = request.GET.get("access_token")
            token.username = request.GET.get("user_name")
            token.save()

        case "lightmetrics":
            raise NotImplementedError

        case _:
            return HttpResponse(status=400)

    context = {
        "user": user,
        "token": token,
        "service": service,
    }

    return render(request, "terminusgps_tracker/oauth2_callback.html", context=context)


def registration(request: HttpRequest, step: str) -> HttpResponse:
    if step == "step_1":
        return registration_step_1(request)
    elif step == "step_2":
        return registration_step_2(request)
    elif step == "step_3":
        return registration_step_3(request)
    elif step == "review":
        return registration_review(request)
    elif step == "success":
        return registration_success(request)
    else:
        return registration(request, step="step_1")


def registration_step_1(request: HttpRequest) -> HttpResponse:
    if not request.method == "POST":
        request.session["imei_number"] = request.GET.get("imei", "")
        form = PersonForm()
    else:
        form = PersonForm(request.POST)
        if form.is_valid():
            request.session["first_name"] = form.cleaned_data["first_name"]
            request.session["last_name"] = form.cleaned_data["last_name"]
            return redirect("/register/step_2/")
    context = {
        "title": "Wialon Registration - Step 1",
        "form": form,
    }
    return render(request, "terminusgps_tracker/register/step_1.html", context=context)


def registration_step_2(request: HttpRequest) -> HttpResponse:
    if "first_name" not in request.session or "last_name" not in request.session:
        return redirect("registration_step_1")
    elif not request.method == "POST":
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            request.session["email"] = form.cleaned_data["email"]
            request.session["phone_number"] = form.cleaned_data["phone_number"]
            return redirect("/register/step_3/")
    context = {
        "title": "Wialon Registration - Step 2",
        "form": form,
    }
    return render(request, "terminusgps_tracker/register/step_2.html", context=context)


def registration_step_3(request: HttpRequest) -> HttpResponse:
    if "email" not in request.session or "phone_number" not in request.session:
        return redirect("registration_step_2")
    elif not request.method == "POST":
        form = AssetForm(initial={"imei_number": request.session["imei_number"]})
    else:
        form = AssetForm(request.POST)
        if form.is_valid():
            request.session["asset_name"] = form.cleaned_data["asset_name"]
            request.session["imei_number"] = form.cleaned_data["imei_number"]
            return redirect("/register/review/")
    context = {
        "title": "Wialon Registration - Step 3",
        "form": form,
    }
    return render(request, "terminusgps_tracker/register/step_3.html", context=context)


def registration_review(request: HttpRequest) -> HttpResponse:
    if "asset_name" not in request.session or "imei_number" not in request.session:
        return redirect("registration_step_3")
    elif not request.method == "POST":
        form = RegistrationForm()
    else:
        form = RegistrationForm(
            first_name=request.session["first_name"],
            last_name=request.session["last_name"],
            email=request.session["email"],
            phone_number=request.session["phone_number"],
            asset_name=request.session["asset_name"],
            imei_number=request.session["imei_number"],
        )
        if form.is_valid():
            # Create the asset and finish the registration
            return redirect("/register/success/")
    context = {
        "title": "Wialon Registration - Review",
        "form": form,
    }
    return render(request, "terminusgps_tracker/register/review.html", context=context)


def registration_success(request: HttpRequest) -> HttpResponse:
    context = {
        "title": "Wialon Registration Success",
        "message": "You're good to go! Redirecting to Wialon...",
    }
    return render(request, "terminusgps_tracker/register/success.html", context=context)


@requires_wialon_token
def search_wialon(request: HttpRequest) -> HttpResponse:
    token = WialonToken.objects.get(user=request.user).access_token
    with WialonSession(token=token) as session:
        query = WialonQuery(prop_name="sys_user")
        items = query.execute(session).get("items", [])
        context = {
            "title": "Search Results",
            "items": items,
        }
    return render(request, "terminusgps_tracker/search_wialon.html", context=context)


@requires_wialon_token
def search(request: HttpRequest) -> HttpResponse:
    search = request.POST.get("search", "*")
    token = WialonToken.objects.get(user=request.user).access_token
    with WialonSession(token=token) as session:
        query = WialonQuery()
        query.prop_value_mask = search
        items = query.execute(session).get("items", [])
    context = {
        "items": items,
    }
    return render(request, "terminusgps_tracker/_wialon_results.html", context=context)
