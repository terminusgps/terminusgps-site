from . import SquareSession

class SquarePayments(SquareSession):
    def __init__(self) -> None:
        super().__init__()
        self.payments = self.client.payments

    def make_payment(self) -> None:
        params = {
            "idempotency_key": "dd9bdcf4-355e-479d-ac71-4d52863cf089",
            "amount_money": {
                "amount": 1000,
                "currency": "USD"
            },
            "source_id": "cnon:card-nonce-ok",
            "accept_partial_authorization": False,
            "autocomplete": True,
            "billing_address": {
                "address_line_1": "123 Main Street",
                "country": "US",
                "first_name": "John",
                "last_name": "Doe",
                "locality": "San Francisco",
                "postal_code": "94114",
            },
            "buyer_email_address": "john@doe.com",
        }

        return self.payments.create_payment(params)
