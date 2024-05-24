from typing import Union
from .session import SquareSession


class SquareCustomer:
    def __init__(
        self,
        given_name: str,
        family_name: str,
        company_name: str,
        email_address: str,
        phone_number: str,
    ) -> None:
        self.given_name = given_name
        self.family_name = family_name
        self.company_name = company_name
        self.email_address = email_address
        self.phone_number = phone_number

        self.session = SquareSession()

        return None

    def _get_customer(self) -> Union[dict, None]:
        return None

    def _create_customer(self) -> dict:
        return self.session.client.customers.create_customer(
            {
                "given_name": self.given_name,
                "family_name": self.family_name,
                "company_name": self.company_name,
                "email_address": self.email_address,
                "phone_number": self.phone_number,
            }
        ).body

    def _list_customers(self) -> dict:
        return self.session.client.customers.list_customers().body
