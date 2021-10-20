from django.db import models


class Product(models.Model):
    title = models.CharField(verbose_name='title of product', max_length=255)
    cost = models.DecimalField(verbose_name='self cost of product', max_digits=10, decimal_places=2)
    price = models.DecimalField(verbose_name='price of product', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(verbose_name='quantity of product', default=0)

    def __str__(self):
        return self.title


class Order(models.Model):
    products = models.ManyToManyField(Product,
                                      verbose_name='products in order',
                                      related_name='orders',
                                      through='ProductsInOrder',
                                      through_fields=('order', 'product'),
                                      blank=True
                                      )
    created_at = models.DateTimeField(verbose_name='when order is created', auto_now=True)
    total_price = models.DecimalField(verbose_name='sum prices of products in order', max_digits=10, decimal_places=2,
                                      blank=True, default=0)
    STATUSES = (
        (1, 'PAID'),
        (2, 'UNPAID'),
        (3, 'CANCELED'),
        (4, 'RETURNED'),
    )
    status = models.IntegerField(verbose_name='status order', choices=STATUSES, default=2)

    def __str__(self):
        return f"Order №{self.pk}, total price - {self.total_price}, status - {self.status}"


class ProductsInOrder(models.Model):
    """Extra table for M2M"""
    order = models.ForeignKey(Order,
                              verbose_name='order',
                              on_delete=models.CASCADE,
                              related_name='products_in_order')
    product = models.ForeignKey(Product,
                                verbose_name='product',
                                on_delete=models.CASCADE,
                                related_name='products_in_order')
    quantity = models.PositiveIntegerField(verbose_name='quantity', default=1)
    total_cost_by_qty = models.DecimalField(verbose_name='sum self cost of one type of products in order',
                                            max_digits=10,
                                            decimal_places=2,
                                            blank=True)
    total_price_by_qty = models.DecimalField(verbose_name='sum price of one type of products in order',
                                             max_digits=10,
                                             decimal_places=2,
                                             blank=True)

    def save(self, *args, **kwargs):
        self.total_price_by_qty = self.product.price * self.quantity
        self.total_cost_by_qty = self.product.cost * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} products {self.product.title} in order №{self.order.pk}"
