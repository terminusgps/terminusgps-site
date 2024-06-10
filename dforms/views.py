from django.http import JsonResponse
from django.shortcuts import render

from .forms import WialonRegistration


def register(request):
    if request.method == "POST":
        form = WialonRegistration(request.POST)
        context = {"form": form}
        if form.is_valid():
            response = {"success": True, "message": "Form submitted successfully."}
        else:
            response = {
                "success": False,
                "form_html": render(
                    request, "dforms/partials/field.html", context=context
                ),
            }
        return JsonResponse(response)
    else:
        form = WialonRegistration()
        context = {"form": form}
    return render(request, "dforms/form_template.html", context=context)
