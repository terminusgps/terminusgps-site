from functools import wraps

from django.shortcuts import redirect

from .models import WialonToken


def requires_wialon_token(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        token, created = WialonToken.objects.get_or_create(user=request.user)
        if created:
            return redirect("auth", "wialon")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
