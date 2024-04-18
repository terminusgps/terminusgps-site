from ad_api.api import sponsored_products
from dataclasses import dataclass

result = sponsored_products.Campaigns().list_campaigns()

@dataclass
class Product:
    id: int
    name: str
    description: str
    category: str
    cost: float
    price: float
