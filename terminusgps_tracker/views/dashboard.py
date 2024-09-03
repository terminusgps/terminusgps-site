from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

def dashboard_view(request: HttpRequest) -> HttpResponse:
    context = {"title": "Dashboard"}
    context.update({
        "items": [
            {
                "index": 0,
                "date": "2024-01-01",
                "name": "TLD-1000",
                "description": "A satellite GPS tracking unit with one year of warranty support.",
                "quantity": 1,
                "rate": 50.00,
                "amount": 200.00,
                "tax_rate": 0.10,
                "tax_amount": 20.00,
                "total_amount": 220.00,
            },
            {
                "index": 1,
                "date": "2024-01-02",
                "name": "TLD-1000",
                "description": "A satellite GPS tracking unit with one year of warranty support.",
                "quantity": 1,
                "rate": 50.00,
                "amount": 200.00,
                "tax_rate": 0.10,
                "tax_amount": 20.00,
                "total_amount": 220.00,
            },
            {
                "index": 2,
                "date": "2024-01-03",
                "name": "TLD-1000",
                "description": "A satellite GPS tracking unit with one year of warranty support.",
                "quantity": 1,
                "rate": 50.00,
                "amount": 200.00,
                "tax_rate": 0.10,
                "tax_amount": 20.00,
                "total_amount": 220.00,
            },
            {
                "index": 3,
                "date": "2024-01-04",
                "name": "TLD-1000",
                "description": "A satellite GPS tracking unit with one year of warranty support.",
                "quantity": 1,
                "rate": 50.00,
                "amount": 200.00,
                "tax_rate": 0.10,
                "tax_amount": 20.00,
                "total_amount": 220.00,
            },
            {
                "index": 4,
                "date": "2024-01-05",
                "name": "TLD-1000",
                "description": "A satellite GPS tracking unit with one year of warranty support.",
                "quantity": 1,
                "rate": 50.00,
                "amount": 200.00,
                "tax_rate": 0.10,
                "tax_amount": 20.00,
                "total_amount": 220.00,
            },
        ]
    })
    return render(request, "terminusgps_tracker/dashboard.html", context=context)
