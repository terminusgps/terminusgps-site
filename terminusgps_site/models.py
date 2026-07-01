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

    def email_to_admins(self) -> None:
        template_name = "terminusgps/emails/contact_form_response.txt"
        subject = f"Contact Form Response - {self.name}"
        message = render_to_string(template_name, {"response": self})
        mail_admins(subject, message, fail_silently=True)
