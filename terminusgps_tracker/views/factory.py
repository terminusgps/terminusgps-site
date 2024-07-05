from django.http import HttpRequest, HttpResponse

from terminusgps_tracker.models.forms import RegistrationForm
from terminusgps_tracker.views.forms import RegistrationFormView

FORMS = {
    "registration": (RegistrationForm, RegistrationFormView),
}


def form_view(request: HttpRequest, form_name: str) -> HttpResponse:
    cls, view = FORMS.get(form_name, (None, None))
    if not cls:
        return HttpResponse(status=404)
    return view.as_view()(request)
