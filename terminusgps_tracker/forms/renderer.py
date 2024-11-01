from django.forms.renderers import TemplatesSetting
from django.template.base import Template
from django.conf import settings


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/forms/form.html"
    field_template_name = "terminusgps_tracker/forms/field.html"

    def get_template(self, template_name: str) -> Template | None:
        if settings.DEBUG:
            print(f"Getting template '{template_name}'...")
        if template_name == "django/forms/errors/list/default.html":
            template_name = "terminusgps_tracker/forms/errors.html"
        return super().get_template(template_name)
