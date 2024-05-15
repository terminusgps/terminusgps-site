from ecom.models import Product
from django.forms import ModelForm

from django.utils.translation import gettext_lazy as _


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'desc', 'cost', 'price', 'img']
        labels = {
            "name": _("Product Name"),
            "desc": _("Product Description"),
            "cost": _("Product Cost"),
            "price": _("Product Price"),
            "img": _("Product Main Image"),
        }
        help_text = {
            "name": _("Enter the name of the product."),
            "desc": _("Enter the description of the product."),
            "cost": _("How much the product cost to purchase."),
            "price": _("How much to sell the product for."),
            "img": _("Main image of the product, `.jpg` or `.png` format."),
        }
        error_messages = {
            "name": {
                "required": _("Product name is required."),
                "max_length": _("Product name must be less than 256 characters."),
            },
            "cost": {
                "required": _("Product cost is required."),
                "max_digits": _("Product cost be less than 10 digits."),
                "invalid": _("Product cost must be a number."),
            },
            "price": {
                "required": _("Product price is required."),
                "max_digits": _("Product price be less than 10 digits."),
                "invalid": _("Product price must be a number."),
            },
            "img": {
                "required": _("Product image is required."),
            },
        }

def create_product_form(*args, **kwargs) -> ProductForm:
    return ProductForm(*args, **kwargs)
