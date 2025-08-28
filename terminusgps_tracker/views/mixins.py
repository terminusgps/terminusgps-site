from django.contrib.auth.mixins import UserPassesTestMixin

from terminusgps_tracker.models import Customer


class CustomerAuthenticationRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        customer_pk = self.kwargs.get("customer_pk")
        if customer_pk is None:
            return False

        try:
            customer = Customer.objects.get(pk=customer_pk)
            return (
                self.request.user.is_staff
                or self.request.user.pk == customer.user.pk
            )
        except Customer.DoesNotExist:
            return False
