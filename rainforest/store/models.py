from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Order(models.Model):
    products = models.ManyToManyField(Product,
                                      related_name='orders',
                                      through='ProductsInOrder',
                                      through_fields=('order', 'product'),
                                      null=True,
                                      blank=True
                                      )
    created_at = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    STATUSES = (
        (1, 'PAID'),
        (2, 'UNPAID'),
        (3, 'CANCELED'),
        (4, 'RETURNED'),
    )
    status = models.IntegerField(choices=STATUSES, default=2)

    def __str__(self):
        return f"Order №{self.id}, total price - {self.total_price}, status - {self.status}"


class ProductsInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price_by_qty = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.total_price_by_qty = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} products {self.product.title} in order №{self.order.id}"

