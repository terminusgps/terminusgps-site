from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy

from terminusgps_installer.models import Installer


class InstallerRequiredMixin(UserPassesTestMixin):
    permission_denied_message = "You must be an installer to view this content."
    raise_exception = False
    login_url = reverse_lazy("login")

    def test_func(self) -> bool:
        """Returns :py:obj:`True` if the user has an associated installer, else :py:obj:`False`."""
        try:
            if not hasattr(self, "request") or not hasattr(self.request, "user"):
                return False
            if self.request.user.is_authenticated and self.request.user.is_staff:
                return True
            installer = Installer.objects.get(user=self.request.user)
            return bool(installer)
        except Installer.DoesNotExist:
            return False
