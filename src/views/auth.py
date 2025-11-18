import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_control, cache_page
from django.views.generic import FormView, TemplateView
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.flags import DataFlag
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps.wialon.utils import generate_wialon_password

from .. import tasks
from ..forms import TerminusgpsRegisterForm

logger = logging.getLogger(__name__)


def create_wialon_account(user: AbstractBaseUser, password: str) -> None:
    """Creates a Wialon account in Wialon for the user."""
    with WialonSession(token=settings.WIALON_TOKEN) as session:
        account_user = session.wialon_api.core_create_user(
            **{
                "creatorId": settings.WIALON_ADMIN_ID,
                "name": f"super_{user.username}",
                "password": generate_wialon_password(),
                "dataFlags": DataFlag.USER_BASE,
            }
        )["item"]
        resource = session.wialon_api.core_create_resource(
            **{
                "creatorId": settings.WIALON_ADMIN_ID,
                "name": f"account_{user.username}",
                "dataFlags": DataFlag.RESOURCE_BASE,
                "skipCreatorCheck": int(True),
            }
        )["item"]
        session.wialon_api.account_create_account(
            **{"itemId": resource["id"], "plan": "terminusgps_ext_hist"}
        )
        session.wialon_api.core_create_user(
            **{
                "creatorId": account_user["id"],
                "name": user.username,
                "password": password,
                "dataFlags": DataFlag.USER_BASE,
            }
        )["item"]


@method_decorator(cache_page(timeout=60 * 15), name="get")
@method_decorator(cache_control(private=True), name="get")
class RegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegisterForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_register.html"
    success_url = reverse_lazy("login")
    template_name = "terminusgps/register.html"

    @transaction.atomic
    def form_valid(self, form: TerminusgpsRegisterForm) -> HttpResponse:
        try:
            now = timezone.now()
            user = get_user_model().objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
            )
            create_wialon_account(user, form.cleaned_data["password1"])
            tasks.send_account_created_email.enqueue(
                email_address=user.username,
                first_name=form.cleaned_data["first_name"],
                create_date=now,
            )
            return super().form_valid(form=form)
        except WialonAPIError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! %(e)s"), code="invalid", params={"e": str(e)}
                ),
            )
            return self.form_invalid(form=form)


@method_decorator(cache_page(timeout=60 * 15), name="get")
@method_decorator(cache_control(private=True), name="get")
class LoginView(HtmxTemplateResponseMixin, LoginViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Login",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_login.html"
    template_name = "terminusgps/login.html"


@method_decorator(cache_page(timeout=60 * 15), name="get")
@method_decorator(cache_control(private=True), name="get")
class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    extra_context = {
        "title": "Logged Out",
        "subtitle": "We know where ours are... do you?",
    }
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps/partials/_logged_out.html"
    template_name = "terminusgps/logged_out.html"


@method_decorator(cache_page(timeout=60 * 15), name="dispatch")
@method_decorator(cache_control(private=True), name="dispatch")
class DashboardView(
    LoginRequiredMixin, HtmxTemplateResponseMixin, TemplateView
):
    content_type = "text/html"
    extra_context = {
        "title": "Dashboard",
        "subtitle": "You'll know where yours are...",
    }
    http_method_names = ["get"]
    partial_template_name = "terminusgps/partials/_dashboard.html"
    template_name = "terminusgps/dashboard.html"
