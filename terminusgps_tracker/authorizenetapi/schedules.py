from typing import Optional
from datetime import date

from authorizenet.apicontractsv1 import (
    paymentScheduleType,
    ARBSubscriptionUnitEnum,
    paymentScheduleTypeInterval,
)


def create_monthly_schedule(
    total_months: int = 12, trial_months: int = 1, start_date: Optional[date] = None
) -> paymentScheduleType:
    if total_months <= 0 or trial_months <= 0:
        raise ValueError(
            "Both total months and trial months must be positive non-zero integer values."
        )
    return paymentScheduleType(
        interval=paymentScheduleTypeInterval(
            length=1, unit=ARBSubscriptionUnitEnum.months
        ),
        startDate=start_date if start_date else date.today(),
        totalOccurances=total_months,
        trialOccurances=trial_months,
    )


def create_annual_schedule(
    total_years: int = 2, start_date: Optional[date] = None
) -> paymentScheduleType:
    if total_years <= 0:
        raise ValueError(
            f"Invalid total years: '{total_years}'. Total years must be a positive non-zero integer."
        )
    elif total_years > 99:
        raise ValueError(
            f"Invalid total years: '{total_years}'. Total years cannot be greater than 99."
        )
    return paymentScheduleType(
        interval=paymentScheduleTypeInterval(
            length=12, unit=ARBSubscriptionUnitEnum.months
        ),
        startDate=start_date if start_date else date.today(),
        totalOccurances=total_years,
    )


def create_quarterly_schedule(
    total_quarters: int = 8, start_date: Optional[date] = None
) -> paymentScheduleType:
    if total_quarters <= 0:
        raise ValueError(
            f"Invalid total quarters: '{total_quarters}'. Total quarters must be a positive non-zero integer."
        )
    elif total_quarters % 4 != 0:
        raise ValueError(
            f"Invalid total quarters: '{total_quarters}'. Total quarters must be evenly divisible by 4."
        )
    return paymentScheduleType(
        interval=paymentScheduleTypeInterval(
            length=3, unit=ARBSubscriptionUnitEnum.months
        ),
        startDate=start_date if start_date else date.today(),
        totalOccurances=total_quarters,
    )
