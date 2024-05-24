from django.db import models
from datetime import datetime

from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    name = models.CharField(max_length=1024)
    desc = models.TextField()
    sku = models.CharField(max_length=12, unique=True, blank=False, null=False)
    source = models.ImageField(upload_to="media/products/")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cat = models.ForeignKey("Category", on_delete=models.CASCADE, null=True, blank=True)
    amazon_link = models.URLField(null=True, blank=True)
    amazon_rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)

    def __str__(self):
        return self.name

    def img(self):
        return self.source.url

    def rating(self):
        return int(self.amazon_rating * 20)


class Category(models.Model):
    class Meta:
        verbose_name_plural = "categories"

    name = models.CharField(max_length=1024)
    desc = models.TextField()
    source = models.ImageField(upload_to="categories/")
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.name

    def url(self):
        return self.source.url


class Cart(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)

    def total(self):
        return sum([p.price for p in self.products.all()])

    def create_order(self):
        order = Order.objects.create(user=self.user, cart=self, total=self.total())
        return order

    def __str__(self):
        return f"{self.user.username}'s Cart"


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        APPROVED = "AP", _("Order was approved by admin")
        CANCELED = "CL", _("Order was canceled by user")
        CANCELED_ADMIN = "CA", _("Order was canceled by admin")
        CREATED = "PD", _("Order was created")
        DECLINED = "DP", _("Order payment was declined")
        DECLINED_ADMIN = "DA", _("Order payment was declined by admin")
        DISPUTED = "DS", _("Order was disputed by user")
        FULFILLED = "FL", _("Order was fulfilled/received by customer")
        REFUNDED_FULL = "RF", _("Order was refunded in full")
        REFUNDED_PARTIAL = "RP", _("Order was refunded in part")
        SHIPPED = "SP", _("Order was shipped but not received")

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=2, default=OrderStatus.CREATED, choices=OrderStatus.choices
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_fulfilled = models.DateTimeField(blank=True, null=True, default=datetime.now)

    def __str__(self):
        return f"{self.cart.user.username}'s Order"
