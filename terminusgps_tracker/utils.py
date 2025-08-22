import decimal

from django.db import models

from terminusgps_tracker.models import Customer, CustomerWialonUnit


def calculate_tax(
    sub_total: decimal.Decimal,
    tax_rate: decimal.Decimal = decimal.Decimal("0.0825"),
) -> decimal.Decimal:
    """Multiplies ``sub_total`` by ``tax_rate`` and returns the product."""
    return sub_total * tax_rate


def calculate_sub_total(customer: Customer) -> decimal.Decimal:
    """Returns an aggregate sum of the customer's Wialon unit costs."""
    aggregate_sum = CustomerWialonUnit.objects.filter(
        customer=customer
    ).aggregate(models.Sum("tier__price"))
    return round(aggregate_sum["tier__price__sum"], 2)


def calculate_grand_total(
    sub_total: decimal.Decimal, tax: decimal.Decimal
) -> decimal.Decimal:
    """Adds ``sub_total`` and ``tax`` rounded to 2 decimal places and returns the sum."""
    return round(sub_total + tax, 2)
