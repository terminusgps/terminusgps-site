import functools

from django.core.mail import mail_admins
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class ContactFormResponse(models.Model):
    name = models.CharField(max_length=64)
    email = models.EmailField(max_length=255)
    message = models.TextField(max_length=2048)
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("contact form response")
        verbose_name_plural = _("contact form responses")

    def __str__(self) -> str:
        return str(self.name)

    @functools.cached_property
    def admin_email_message(self) -> str:
        # TODO: Refactor this template name... maybe to a setting
        template_name = "terminusgps/emails/contact_form_response.txt"
        message = render_to_string(template_name, {"response": self})
        return message

    @functools.cached_property
    def admin_email_subject(self) -> str:
        return f"Contact Form Response - {self}"

    def email_to_admins(self) -> None:
        mail_admins(
            self.admin_email_subject,
            self.admin_email_message,
            fail_silently=True,
        )
