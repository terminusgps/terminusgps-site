from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from terminusgps.wialon import constants
from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerRegisterForm
from terminusgps_tracker.models.customers import Customer
from terminusgps_tracker.views.mixins import HtmxTemplateResponseMixin


class TrackerLoginView(HtmxTemplateResponseMixin, LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
        "class": "p-4 flex flex-col gap-2",
    }
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("dashboard")
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("dashboard")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(HtmxTemplateResponseMixin, LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("login")
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps_tracker/logout.html"


class TrackerRegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
        "class": "p-4 flex flex-col gap-2",
    }
    form_class = TrackerRegisterForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps_tracker/register.html"
    partial_template_name = "terminusgps_tracker/partials/_register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(
        self, form: TrackerRegisterForm
    ) -> HttpResponse | HttpResponseRedirect:
        try:
            ids = self.wialon_registration_flow(form)
            Customer.objects.create(
                user=get_user_model().objects.create_user(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"],
                ),
                wialon_end_user_id=ids.get("end_user_id"),
                wialon_super_user_id=ids.get("super_user_id"),
                wialon_group_id=ids.get("group_id"),
                wialon_resource_id=ids.get("resource_id"),
            )
        except WialonError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(error)s"), code="invalid", params={"error": e}
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)

    @staticmethod
    def wialon_registration_flow(
        form: TrackerRegisterForm,
    ) -> dict[str, str | int | None]:
        username: str = form.cleaned_data["username"]
        password: str = form.cleaned_data["password1"]

        with WialonSession() as session:
            super_user = WialonUser(
                id=None,
                session=session,
                creator_id=settings.WIALON_ADMIN_ID,
                name=f"super_{username}",  # super_email@domain.com
                password=password,
            )
            resource = WialonResource(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=f"account_{username}",  # account_email@domain.com
            )
            end_user = WialonUser(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=username,  # email@domain.com
                password=password,
            )
            unit_group = WialonUnitGroup(
                id=None,
                session=session,
                creator_id=super_user.id,
                name=f"group_{username}",  # group_email@domain.com
            )

            end_user.grant_access(
                unit_group, access_mask=constants.ACCESSMASK_UNIT_BASIC
            )
            end_user.grant_access(
                resource, access_mask=constants.ACCESSMASK_RESOURCE_BASIC
            )
            resource.create_account("terminusgps_ext_hist")
            resource.enable_account()
            resource.set_settings_flags()
            resource.add_days(7)

        return {
            "end_user_id": end_user.id,
            "group_id": unit_group.id,
            "resource_id": resource.id,
            "super_user_id": super_user.id,
        }
