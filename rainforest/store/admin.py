from django.contrib import admin

from .models import Order, Product, ProductsInOrder

admin.site.register(Order)
admin.site.register(Product)
admin.site.register(ProductsInOrder)

