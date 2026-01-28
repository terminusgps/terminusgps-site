import datetime

from django.conf import settings
from django.contrib.auth.views import LoginView as LoginViewBase
from django.contrib.auth.views import LogoutView as LogoutViewBase
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import FormView
from terminusgps.authorizenet.service import (
    AuthorizenetControllerExecutionError,
)
from terminusgps.mixins import HtmxTemplateResponseMixin
from terminusgps.wialon.session import WialonAPIError, WialonSession
from terminusgps.wialon.utils import generate_wialon_password
from terminusgps_payments.models import CustomerProfile

from terminusgps_manager.models import (
    TerminusGPSCustomer,
    WialonAccount,
    WialonUser,
)

from ..forms import TerminusgpsAuthenticationForm, TerminusgpsRegistrationForm
from ..tasks import send_email


@transaction.atomic
def wialon_registration_flow(
    form: TerminusgpsRegistrationForm, customer: TerminusGPSCustomer
) -> None:
    with WialonSession(token=settings.WIALON_TOKEN) as session:
        # Create account user
        super_user_data = session.wialon_api.core_create_user(
            **{
                "creatorId": settings.WIALON_ADMIN_ID,
                "name": f"super_{form.cleaned_data['username']}",
                "password": generate_wialon_password(),
                "dataFlags": 1,
            }
        )
        super_user = WialonUser()
        super_user.pk = int(super_user_data["item"]["id"])
        super_user.save()

        # Create resource
        resource_data = session.wialon_api.core_create_resource(
            **{
                "creatorId": super_user.pk,
                "name": f"account_{form.cleaned_data['username']}",
                "skipCreatorCheck": int(True),
                "dataFlags": 1,
            }
        )
        # Create account from resource
        session.wialon_api.account_create_account(
            **{
                "itemId": int(resource_data["item"]["id"]),
                "plan": "terminusgps_ext_hist",
            }
        )
        account = WialonAccount()
        account.pk = int(resource_data["item"]["id"])
        account.save()

        # Enable account and clear flags
        account.enable(session)
        account.update_flags(session, flags=-0x20)

        # Create end user
        end_user_data = session.wialon_api.core_create_user(
            **{
                "creatorId": super_user.pk,
                "name": form.cleaned_data["username"],
                "password": form.cleaned_data["password1"],
                "dataFlags": 1,
            }
        )
        end_user = WialonUser()
        end_user.pk = int(end_user_data["item"]["id"])
        end_user.save()

        # Disable account, enabled by subscribing
        account.disable(session)

        # Assign to objects to customer
        customer.wialon_user = end_user
        customer.wialon_account = account
        customer.save(update_fields=["wialon_user", "wialon_account"])


@method_decorator(never_cache, name="dispatch")
class LoginView(HtmxTemplateResponseMixin, LoginViewBase):
    content_type = "text/html"
    extra_context = {"title": "Login"}
    form_class = TerminusgpsAuthenticationForm
    http_method_names = ["get", "post"]
    template_name = "terminusgps/login.html"


class LogoutView(HtmxTemplateResponseMixin, LogoutViewBase):
    content_type = "text/html"
    extra_context = {"title": "Logged Out"}
    http_method_names = ["get", "post"]
    template_name = "terminusgps/logged_out.html"


@method_decorator(never_cache, name="dispatch")
class RegisterView(HtmxTemplateResponseMixin, FormView):
    content_type = "text/html"
    extra_context = {
        "title": "Register",
        "subtitle": "You'll know where yours are...",
    }
    form_class = TerminusgpsRegistrationForm
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("login")
    template_name = "terminusgps/register.html"

    @transaction.atomic
    def form_valid(self, form: TerminusgpsRegistrationForm) -> HttpResponse:
        try:
            user = form.save(commit=True)
            user.email = form.cleaned_data["username"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()

            customer_profile = CustomerProfile(user=user)
            customer_profile.email = user.email
            customer_profile.merchant_id = (
                f"{user.first_name} {user.last_name}"
            )
            customer_profile.save()

            customer = TerminusGPSCustomer()
            customer.user = user
            customer.save()
            wialon_registration_flow(form, customer)
            send_email.enqueue(
                to=[user.email],
                subject="Terminus GPS - Account Created",
                template_name="terminusgps/emails/account_created.txt",
                html_template_name="terminusgps/emails/account_created.html",
                context={
                    "fn": user.first_name,
                    "date": datetime.date.today().strftime("%Y-%m-%d"),
                    "platform_link": "https://hosting.terminusgps.com",
                    "support_link": "mailto:support@terminusgps.com",
                    "contact_link": "https://app.terminusgps.com/contact/",
                    "subscribing_link": "https://app.terminusgps.com/subscriptions/",
                },
            )
            return super().form_valid(form=form)
        except (AuthorizenetControllerExecutionError, WialonAPIError) as error:
            form.add_error(None, ValidationError(str(error), code="invalid"))
            return self.form_invalid(form=form)
