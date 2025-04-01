from django.db.models import BaseConstraint


class ExclusiveCustomerPaymentConstraint(BaseConstraint):
    name = "%(app_label)s_%(class)s_exclusive_customer_payment"
    violation_error_code = "invalid"


class ExclusiveCustomerAddressConstraint(BaseConstraint):
    name = "%(app_label)s_%(class)s_exclusive_customer_address"
    violation_error_code = "invalid"
