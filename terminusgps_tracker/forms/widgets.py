from django.forms import widgets


class TrackerTextInput(widgets.TextInput):
    input_type = "text"
    template_name = "terminusgps_tracker/forms/widgets/text.html"


class TrackerSelectInput(widgets.Select):
    template_name = "terminusgps_tracker/forms/widgets/select.html"


class TrackerInput(widgets.Input):
    template_name = "terminusgps_tracker/forms/widgets/input.html"


class TrackerPasswordInput(widgets.Input):
    input_type = "password"
    template_name = "terminusgps_tracker/forms/widgets/password.html"


class TrackerDateInput(widgets.DateInput):
    input_type = "date"
    template_name = "terminusgps_tracker/forms/widgets/date.html"


class TrackerNumberInput(widgets.NumberInput):
    input_type = "number"
    template_name = "terminusgps_tracker/forms/widgets/number.html"


class TrackerEmailInput(widgets.EmailInput):
    input_type = "email"
    template_name = "terminusgps_tracker/forms/widgets/email.html"
