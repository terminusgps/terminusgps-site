from django.db.models import BaseConstraint


class ExclusiveCustomerPaymentConstraint(BaseConstraint):
    name = "exclusive_customer_payment"
    violation_error_code = "invalid"


class ExclusiveCustomerAddressConstraint(BaseConstraint):
    name = "exclusive_customer_address"
    violation_error_code = "invalid"
