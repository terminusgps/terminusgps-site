from django.forms.renderers import TemplatesSetting


class TerminusFormRenderer(TemplatesSetting):
    form_template_name = "terminusgps_tracker/partials/_form_snippet.html"
    field_template_name = "terminusgps_tracker/partials/_field_snippet.html"
