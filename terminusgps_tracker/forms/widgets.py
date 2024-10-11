from django.forms.widgets import Input, Select


class CustomTextInput(Input):
    input_type = "text"
    template_name = ""


class CustomPasswordInput(Input):
    input_type = "password"
    template_name = ""


class CustomEmailInput(Input):
    input_type = "email"
    template_name = ""


class CustomSelectInput(Select):
    input_type = "text"
    template_name = "terminusgps_tracker/partials/_select.html"
