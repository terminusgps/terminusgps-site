from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from terminusgps.wialon.items import WialonResource, WialonUnitGroup, WialonUser
from terminusgps.wialon.session import WialonSession
from wialon.api import WialonError

from terminusgps_tracker.forms import TrackerAuthenticationForm, TrackerSignupForm
from terminusgps_tracker.models import TrackerProfile, TrackerSubscription


class TrackerLoginView(LoginView):
    authentication_form = TrackerAuthenticationForm
    content_type = "text/html"
    extra_context = {"title": "Login", "subtitle": "We know where ours are... do you?"}
    http_method_names = ["get", "post"]
    next_page = reverse_lazy("tracker profile")
    partial_template_name = "terminusgps_tracker/partials/_login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("tracker profile")
    template_name = "terminusgps_tracker/login.html"


class TrackerLogoutView(LogoutView):
    content_type = "text/html"
    extra_context = {"title": "Logout"}
    http_method_names = ["get", "post", "options"]
    next_page = reverse_lazy("tracker login")
    partial_template_name = "terminusgps_tracker/partials/_logout.html"
    success_url_allowed_hosts = settings.ALLOWED_HOSTS
    template_name = "terminusgps_tracker/logout.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        if request.headers.get("HX-Request"):
            self.template_name = self.partial_template_name


class TrackerSignupView(SuccessMessageMixin, FormView):
    content_type = "text/html"
    extra_context = {"title": "Sign Up", "subtitle": "You'll know where yours are..."}
    form_class = TrackerSignupForm
    http_method_names = ["get", "post"]
    partial_template_name = "terminusgps_tracker/partials/_signup.html"
    success_message = "%(username)s's account was created succesfully"
    success_url = reverse_lazy("tracker login")
    template_name = "terminusgps_tracker/signup.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        if not hasattr(settings, "WIALON_TOKEN"):
            raise ImproperlyConfigured("'WIALON_TOKEN' setting is required.")
        if not hasattr(settings, "WIALON_ADMIN_ID"):
            raise ImproperlyConfigured("'WIALON_ADMIN_ID' setting is required.")
        return super().setup(request, *args, **kwargs)

    def get_success_message(self, cleaned_data: dict[str, Any]) -> str:
        return self.success_message % dict(
            cleaned_data, username=cleaned_data.get("username", "")
        )

    def form_invalid(self, form: TrackerSignupForm) -> HttpResponse:
        response = super().form_invalid(form=form)
        response.headers["HX-Request"] = True
        return response

    def form_valid(self, form: TrackerSignupForm) -> HttpResponse:
        try:
            ids = self.wialon_registration_flow(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form=form)
        else:
            user = get_user_model().objects.create_user(
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["username"],
            )
            self.profile = TrackerProfile.objects.create(user=user)
            TrackerSubscription.objects.create(profile=self.profile)
            self.profile.wialon_end_user_id = ids.get("end_user")
            self.profile.wialon_group_id = ids.get("group")
            self.profile.wialon_resource_id = ids.get("resource")
            self.profile.save()
        response = super().form_valid(form=form)
        response.headers["HX-Request"] = True
        return response

    def wialon_registration_flow(self, username: str, password: str) -> dict:
        with WialonSession(token=settings.WIALON_TOKEN) as session:
            admin_id = settings.WIALON_ADMIN_ID
            resource = self._wialon_create_resource(admin_id, username, session)
            self._wialon_create_account(resource.id, session=session)
            end_user = self._wialon_create_user(admin_id, username, password, session)
            group = self._wialon_create_group(admin_id, f"group_{username}", session)

            return {"end_user": end_user.id, "group": group.id, "resource": resource.id}

    @staticmethod
    def _wialon_create_account(
        resource_id: int | None,
        session: WialonSession,
        plan: str = "terminusgps_ext_hist",
    ) -> None:
        try:
            if resource_id is None:
                raise ValueError

            session.wialon_api.account_create_account(
                **{"itemId": str(resource_id), "plan": plan}
            )
            session.wialon_api.account_enable_account(
                **{"itemId": str(resource_id), "enable": str(int(False))}
            )
        except (WialonError, ValueError) as e:
            print(e)
            raise ValidationError(
                _("Whoops! Failed to create Wialon account: #'%(value)s'"),
                code="wialon",
                params={"value": resource_id},
            )

    @staticmethod
    def _wialon_create_resource(
        creator_id: int | None, name: str, session: WialonSession
    ) -> WialonResource:
        try:
            if creator_id is None:
                raise ValueError

            resource = WialonResource(creator_id=creator_id, name=name, session=session)
            return resource
        except (WialonError, ValueError) as e:
            print(e)
            raise ValidationError(
                _("Whoops! Failed to create Wialon resource: '%(value)s'"),
                code="wialon",
                params={"value": name},
            )

    @staticmethod
    def _wialon_create_group(
        creator_id: int, name: str, session: WialonSession
    ) -> WialonUnitGroup:
        try:
            group = WialonUnitGroup(creator_id=creator_id, name=name, session=session)
            return group
        except (WialonError, ValueError):
            raise ValidationError(
                _("Whoops! Failed to create Wialon group: '%(value)s'"),
                code="wialon",
                params={"value": name},
            )

    @staticmethod
    def _wialon_create_user(
        creator_id: int, username: str, password: str, session: WialonSession
    ) -> WialonUser:
        try:
            user = WialonUser(
                creator_id=creator_id, name=username, password=password, session=session
            )
            return user
        except (WialonError, ValueError):
            raise ValidationError(
                _("Whoops! Failed to create Wialon user: '%(value)s'"),
                code="wialon",
                params={"value": username},
            )

    @staticmethod
    def _wialon_get_user(user_id: int, session: WialonSession) -> WialonUser:
        try:
            user = WialonUser(id=str(user_id), session=session)
            return user
        except (WialonError, ValueError):
            raise ValidationError(
                _("Whoops! Failed to retrieve Wialon user: #'%(value)s'"),
                code="wialon",
                params={"value": user_id},
            )
