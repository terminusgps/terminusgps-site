from django.views.generic import FormView

from terminusgps_tracker.models.forms import RegistrationForm

class RegistrationFormView(FormView):
    form_class = RegistrationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/forms/form_registration.html"
    success_url = "/forms/success/"

    def get_initial(self) -> dict:
        initial = super().get_initial()
        if "imei" in self.request.GET:
            initial["imei_number"] = self.request.GET.get("imei", "")
        return initial
