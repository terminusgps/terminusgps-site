from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Product({self.id = }, {self.name = }, {self.desc = }, {self.cost = }, {self.price = })"

    def profit(self) -> float:
        return self.price - self.cost

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"User({self.id = }, {self.name = }, {self.email = })"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    date_created = models.DateTimeField(auto_now_add=True)
    date_fulfilled = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Order #{self.id} by {self.user.name} created {self.date_created}"

    def __repr__(self) -> str:
        return f"Order({self.id = }, {self.user = }, {self.products = }, {self.date_created = }, {self.date_fulfilled = })"
