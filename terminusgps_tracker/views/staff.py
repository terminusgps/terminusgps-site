from boto3.session import Session
from botocore.exceptions import ClientError

from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.views.generic import FormView, TemplateView
from django.utils.translation import gettext_lazy as _
from terminusgps_tracker.forms import EmailTemplateUploadForm
from terminusgps_tracker.views.mixins import HtmxMixin, StaffRequiredMixin


class EmailTemplateRendererView(TemplateView, StaffRequiredMixin):
    extra_context = {
        "title": "Email Renderer",
        "subtitle": "Preview an email template before upload",
        "now": timezone.now(),
        "email": "blake@terminusgps.com",
        "email_template": "terminusgps_tracker/emails/signup_success.html",
    }
    template_name = "terminusgps_tracker/emails/renderer.html"
    http_method_names = ["get"]


class EmailTemplateUploadView(FormView, StaffRequiredMixin, HtmxMixin):
    extra_context = {
        "title": "Upload Email Template",
        "subtitle": "Add a name, subject line and file, then click submit!",
        "class": "p-8 bg-gray-200 rounded border border-terminus-black",
    }
    form_class = EmailTemplateUploadForm
    http_method_names = ["get", "post"]
    partial_template_name = (
        "terminusgps_tracker/staff/partials/_email_template_upload.html"
    )
    template_name = "terminusgps_tracker/staff/email_template_upload.html"

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.boto3_session = self.kwargs.get("boto3_session") or Session().client(
            service_name="ses"
        )

    def form_valid(self, form: EmailTemplateUploadForm) -> HttpResponse:
        try:
            self.boto3_session.create_template(
                **{
                    "Template": {
                        "TemplateName": form.cleaned_data["name"],
                        "SubjectPart": form.cleaned_data["subject"],
                        "TextPart": form.cleaned_data["text_content"],
                        "HtmlPart": form.cleaned_data["html_content"],
                    }
                }
            )
        except ClientError as e:
            form.add_error(
                None,
                ValidationError(
                    _("Whoops! '%(err)s'"), code="invalid", params={"err": e}
                ),
            )
            return self.form_invalid(form=form)
        return super().form_valid(form=form)
