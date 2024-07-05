from django.http import HttpRequest, HttpResponse

from .forms import (AssetFormView, ContactFormView, PersonFormView,
                    RegistrationFormView)

FORM_VIEWS = {
    "asset": (AssetFormView, AssetFormView.as_view()),
    "contact": (ContactFormView, ContactFormView.as_view()),
    "person": (PersonFormView, PersonFormView.as_view()),
    "registration": (RegistrationFormView, RegistrationFormView.as_view()),
}


def form_factory(request: HttpRequest, form_name: str) -> HttpResponse:
    view_class, view = FORM_VIEWS.get(form_name, (None, None))
    if not view_class:
        return HttpResponse(status=404)
    else:
        return view(request)
