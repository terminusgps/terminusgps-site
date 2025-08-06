from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy

from terminusgps_tracker.models import Customer


class CustomerOrStaffRequiredMixin(UserPassesTestMixin):
    login_url = reverse_lazy("login")
    permission_denied_message = "You aren't permitted to view this content."
    raise_exception = True

    def test_func(self) -> bool:
        if self.request.user.is_staff:
            return True

        if not self.request.user.is_authenticated:
            return False

        customer_pk = self.kwargs.get("customer_pk")
        if not customer_pk:
            return False

        try:
            customer = Customer.objects.get(pk=customer_pk)
            return self.request.user.pk == customer.user.pk
        except Customer.DoesNotExist:
            return False
