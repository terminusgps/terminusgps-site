from typing import Any
from django import forms
from django.forms import widgets
from django.views.generic import FormView
from django.http import HttpRequest, HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from terminusgps.wialon.utils import get_id_from_iccid, gen_wialon_password
from terminusgps.wialon.items import WialonUnit, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession

from terminusgps_tracker.validators import (
    validate_wialon_imei_number,
    validate_wialon_username,
)


class TerminusRegistrationForm(forms.Form):
    default_css_class = "m-4 p-4 bg-white text-gray-800 dark:bg-gray-700 dark:text-white rounded w-full border border-gray-300 dark:border-gray-600"

    imei_number = forms.CharField(
        widget=widgets.TextInput(
            attrs={"placeholder": "IMEI #", "class": default_css_class}
        ),
        validators=[validate_wialon_imei_number],
    )
    email = forms.CharField(
        widget=widgets.TextInput(
            attrs={"placeholder": "Email", "class": default_css_class}
        ),
        validators=[validate_wialon_username],
    )
    phone_number = forms.CharField(
        required=False,
        widget=widgets.TextInput(
            attrs={"placeholder": "Phone #", "class": default_css_class}
        ),
    )


class TerminusRegistrationView(FormView):
    content_type = "text/html"
    extra_context = {
        "title": "New Account",
        "subtitle": "Let's get your account set up!",
    }
    form_class = TerminusRegistrationForm
    http_method_names = ["get", "post"]
    success_url = "https://hosting.terminusgps.com/"
    template_name = "terminusgps/registration.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        self.imei_number = request.GET.get("imei")
        return super().setup(request, *args, **kwargs)

    def form_valid(self, form: TerminusRegistrationForm) -> HttpResponse:
        admin_id: int = settings.WIALON_ADMIN_ID
        imei_number: str = form.cleaned_data["imei_number"]
        username: str = form.cleaned_data["email"]
        password: str = gen_wialon_password(length=32)
        phone_number: str | None = form.cleaned_data["phone_number"]

        with WialonSession(token=settings.WIALON_TOKEN) as session:
            unit_id: str | None = get_id_from_iccid(imei_number, session=session)
            if unit_id is not None:
                user: WialonUser = WialonUser(
                    owner_id=str(admin_id),
                    name=username,
                    password=password,
                    session=session,
                )
                if user.id is not None:
                    self.wialon_remove_unit_from_group(
                        unit_id=int(unit_id),
                        group_id=settings.WIALON_UNACTIVATED_GROUP,
                        session=session,
                    )
                    self.wialon_assign_user_to_unit(
                        unit_id=int(unit_id), user_id=user.id, session=session
                    )
                    self.wialon_assign_phone_to_unit(
                        unit_id=int(unit_id), phone_number=phone_number, session=session
                    )
                    self.send_credentials_email(username, password)
        return super().form_valid(form=form)

    def get_initial(self) -> dict[str, Any]:
        initial: dict[str, Any] = super().get_initial()
        initial["imei_number"] = self.imei_number
        return initial

    @classmethod
    def wialon_remove_unit_from_group(
        cls, unit_id: int, group_id: int, session: WialonSession
    ) -> None:
        unit: WialonUnit = WialonUnit(id=str(unit_id), session=session)
        group: WialonUnitGroup = WialonUnitGroup(id=str(group_id), session=session)
        group.rm_item(unit)

    @classmethod
    def wialon_assign_phone_to_unit(
        cls, unit_id: int, session: WialonSession, phone_number: str | None = None
    ) -> None:
        if phone_number:
            unit: WialonUnit = WialonUnit(id=str(unit_id), session=session)
            unit.assign_phone(phone_number)

    @classmethod
    def wialon_assign_user_to_unit(
        cls, unit_id: int, user_id: int, session: WialonSession
    ) -> None:
        unit: WialonUnit = WialonUnit(id=str(unit_id), session=session)
        user: WialonUser = WialonUser(id=str(user_id), session=session)
        user.assign_item(unit)

    @classmethod
    def send_credentials_email(cls, email_addr: str, password: str) -> None:
        subject: str = "Terminus GPS - Your new account credentials"
        text_content: str = render_to_string(
            "terminusgps/emails/credentials.txt",
            context={"username": email_addr, "password": password},
        )
        html_content: str = render_to_string(
            "terminusgps/emails/credentials.html",
            context={"username": email_addr, "password": password},
        )

        email: EmailMultiAlternatives = EmailMultiAlternatives(
            subject, text_content, to=[email_addr]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
